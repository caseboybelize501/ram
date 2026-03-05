from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.reranker import rerank_results
import requests


class AnswerGenerator:
    def __init__(self, retriever):
        self.retriever = retriever

    async def generate_answer(self, question):
        # Retrieve relevant chunks
        retrieved_chunks = await self.retriever.retrieve(question)
        
        # Rerank results
        reranked_chunks = rerank_results(question, retrieved_chunks)
        
        # Format context for LLM
        context = ""
        sources = set()
        for chunk in reranked_chunks:
            context += f"{chunk['text']} (source: {chunk['metadata']['source']}, date: {chunk['metadata']['date']})\n\n"
            sources.add(chunk['metadata']['source'])
        
        # Call local LLaMA model
        answer = self._call_llama(question, context)
        
        return {
            "answer": answer,
            "sources": list(sources),
            "chunks": reranked_chunks
        }

    def _call_llama(self, question, context):
        # This would call your local LLaMA inference endpoint
        prompt = f"You are the user's personal AI assistant with access to their memory.\nAnswer this question using ONLY the provided memory context.\nQuestion: {question}\nRetrieved memory context:\n{context}\nInstructions:\n- Ground every claim in the provided context\n- Cite sources inline as (Source: [SOURCE], [DATE])\n- If context is insufficient, say so explicitly\n- Do not hallucinate facts not in the context\n- Be conversational but precise"
        
        # In practice, this would make an HTTP request to your local LLaMA server
        return "Sample answer based on retrieved context."

    def _format_citation(self, source, date):
        return f"({source}, {date})"