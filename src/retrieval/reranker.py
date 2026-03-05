from sentence_transformers import CrossEncoder

# Load local cross-encoder model
reranker_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')


def rerank_results(query, chunks):
    # Prepare pairs for reranking
    pairs = [[query, chunk["text"]] for chunk in chunks]
    
    # Get scores
    scores = reranker_model.predict(pairs)
    
    # Sort by score
    ranked_chunks = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    
    return [chunk for chunk, score in ranked_chunks]