import chromadb
from chromadb.config import Settings
import os
from sentence_transformers import SentenceTransformer

# Initialize local ChromaDB client
chroma_client = chromadb.PersistentClient(path=os.path.expanduser('~/.personalai/chroma'))

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')


class ChromaStore:
    def __init__(self):
        self.collection = chroma_client.get_or_create_collection("memory")

    def add_chunk(self, chunk_data):
        # Generate embedding for the text
        embedding = model.encode(chunk_data["text"])
        
        # Add to ChromaDB
        self.collection.add(
            documents=[chunk_data["text"]],
            embeddings=[embedding],
            metadatas=[{
                "source": chunk_data["source"],
                "source_url": chunk_data["source_url"],
                "date": chunk_data["date"],
                "entities": chunk_data["entities"]
            }],
            ids=[f"chunk_{len(self.collection.get())}"]
        )

    def search(self, query, top_k=20):
        # Generate embedding for query
        query_embedding = model.encode(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas"]
        )
        
        return results

    def get_timeline(self, filters):
        # Return chronological memory feed
        all_docs = self.collection.get(include=["metadatas"])
        return {
            "items": all_docs["metadatas"],
            "total": len(all_docs["metadatas"])
        }

    def pin_chunk(self, chunk_id):
        # Mark a chunk as important
        pass