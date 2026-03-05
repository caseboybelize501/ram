import time
import asyncio
from src.storage.chroma_store import ChromaStore
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')


class ContextWatcher:
    def __init__(self):
        self.chroma_store = ChromaStore()
        self.last_surface_time = {}
        self.cooldown_period = 3600  # 1 hour in seconds

    async def watch_context(self):
        while True:
            try:
                # Get active window title or clipboard content
                context = self._get_active_context()
                
                if context:
                    await self._check_and_surface(context)
            except Exception as e:
                print(f"Error in context watcher: {e}")
            
            await asyncio.sleep(5)  # Check every 5 seconds

    def _get_active_context(self):
        # In practice, this would use platform-specific APIs
        # For now, return a mock context
        return "Working on project proposal"

    async def _check_and_surface(self, context):
        # Embed current context
        embedding = model.encode(context)
        
        # Search in ChromaDB for similar memories
        results = self.chroma_store.search(context, top_k=5)
        
        if len(results["ids"][0]) > 0:
            # Get first result score
            score = results["distances"][0][0]
            
            if score > 0.82:  # Threshold for relevance
                await self._surface_notification(context, results["documents"][0][0])

    async def _surface_notification(self, context, memory):
        # Check cooldown period
        current_time = time.time()
        
        if memory in self.last_surface_time:
            if current_time - self.last_surface_time[memory] < self.cooldown_period:
                return  # Skip if within cooldown
        
        # In practice, this would show a desktop notification
        print(f"Proactive surface: {context} -> {memory[:100]}...")
        
        # Update last surface time
        self.last_surface_time[memory] = current_time