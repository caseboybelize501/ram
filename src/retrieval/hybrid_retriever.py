from src.storage.chroma_store import ChromaStore
from src.storage.neo4j_store import Neo4jStore
from sentence_transformers import SentenceTransformer
import math

model = SentenceTransformer('all-MiniLM-L6-v2')


class HybridRetriever:
    def __init__(self, chroma_store, graph_store):
        self.chroma_store = chroma_store
        self.graph_store = graph_store

    async def retrieve(self, query, top_k=20):
        # Vector search in ChromaDB
        vector_results = self.chroma_store.search(query, top_k)
        
        # Extract entities from query
        from src.ingestion.entity_extractor import extract_entities
        query_entities = extract_entities(query)
        
        # Graph traversal for related entities
        graph_chunk_ids = []
        for entity in query_entities:
            related_entities = self.graph_store.get_related_entities(entity["text"])
            for rel_entity in related_entities:
                # Get chunks related to this entity (simplified)
                pass  # In practice, you'd query the graph for chunk IDs
        
        # Merge and deduplicate results
        all_chunk_ids = list(set([r["id"] for r in vector_results["ids"][0]] + graph_chunk_ids))
        
        # Apply temporal decay
        final_chunks = []
        for i, chunk_id in enumerate(all_chunk_ids):
            # Get metadata for this chunk
            chunk_metadata = self._get_chunk_metadata(chunk_id)
            days_ago = self._calculate_days_ago(chunk_metadata["date"])
            
            # Apply temporal decay
            score = 1.0 / math.log(days_ago + 2) if days_ago > 0 else 1.0
            final_chunks.append({
                "id": chunk_id,
                "score": score,
                "metadata": chunk_metadata
            })
        
        # Sort by score and return top 5
        final_chunks.sort(key=lambda x: x["score"], reverse=True)
        return final_chunks[:5]

    def _get_chunk_metadata(self, chunk_id):
        # Simplified - in practice this would fetch from ChromaDB
        return {
            "source": "unknown",
            "date": "2023-01-01",
            "text": "Sample text"
        }

    def _calculate_days_ago(self, date_str):
        # Simplified - in practice parse actual dates
        return 30