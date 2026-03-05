import requests
import json

LLAMA_API_URL = "http://localhost:8000/generate"

class LLaMAService:
    def __init__(self):
        pass

    def generate(self, prompt, max_tokens=1024, temperature=0.3):
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stop": ["\n\n"]
        }
        
        try:
            response = requests.post(LLAMA_API_URL, json=payload)
            result = response.json()
            return result["response"]
        except Exception as e:
            print(f"Error calling LLaMA API: {e}")
            return "Error generating response"

    def generate_proactive(self, context, memory):
        prompt = f"The user is currently working on: {context} (from window title/clipboard).\nPotentially relevant memories: {memory[:500]}...\nShould I surface any of these? Return JSON:\n{{ surface: boolean, message: string (under 50 words), relevance_score: 0-100 }}"
        
        payload = {
            "prompt": prompt,
            "max_tokens": 100,
            "temperature": 0.2,
            "stop": ["\n\n"]
        }
        
        try:
            response = requests.post(LLAMA_API_URL, json=payload)
            result = response.json()
            return json.loads(result["response"])
        except Exception as e:
            print(f"Error calling LLaMA API for proactive: {e}")
            return {"surface": False, "message": "Error", "relevance_score": 0}