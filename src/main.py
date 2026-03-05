from fastapi import FastAPI, HTTPException
from src.ingestion.gmail_connector import GmailConnector
from src.ingestion.notion_connector import NotionConnector
from src.ingestion.slack_connector import SlackConnector
from src.ingestion.calendar_connector import CalendarConnector
from src.ingestion.document_processor import DocumentProcessor
from src.ingestion.voice_processor import VoiceProcessor
from src.storage.chroma_store import ChromaStore
from src.storage.neo4j_store import Neo4jStore
from src.retrieval.hybrid_retriever import HybridRetriever
from src.synthesis.answer_generator import AnswerGenerator
from src.proactive.context_watcher import ContextWatcher
import asyncio

app = FastAPI(title="RAM - Personal AI Memory OS")

# Initialize components
chroma_store = ChromaStore()
graph_store = Neo4jStore()
retriever = HybridRetriever(chroma_store, graph_store)
answer_generator = AnswerGenerator(retriever)
context_watcher = ContextWatcher()

# Connectors
gmail_connector = GmailConnector()
notion_connector = NotionConnector()
slack_connector = SlackConnector()
calendar_connector = CalendarConnector()
document_processor = DocumentProcessor()
voice_processor = VoiceProcessor()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/query")
async def query_memory(question: str):
    try:
        result = await answer_generator.generate_answer(question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sync/status")
async def get_sync_status():
    status = {
        "gmail": gmail_connector.get_status(),
        "notion": notion_connector.get_status(),
        "slack": slack_connector.get_status(),
        "calendar": calendar_connector.get_status(),
        "documents": document_processor.get_status(),
        "voice": voice_processor.get_status()
    }
    return status

@app.post("/api/sync/trigger")
async def trigger_sync(source: str):
    if source == "gmail":
        await gmail_connector.sync()
    elif source == "notion":
        await notion_connector.sync()
    elif source == "slack":
        await slack_connector.sync()
    elif source == "calendar":
        await calendar_connector.sync()
    elif source == "documents":
        await document_processor.sync()
    elif source == "voice":
        await voice_processor.sync()
    else:
        raise HTTPException(status_code=400, detail="Invalid source")

@app.get("/api/graph/entities")
async def get_entities():
    return graph_store.get_top_entities()

@app.get("/api/timeline")
async def get_timeline(filters: dict = {}):
    return chroma_store.get_timeline(filters)

@app.post("/api/memory/pin")
async def pin_memory(chunk_id: str):
    chroma_store.pin_chunk(chunk_id)
    return {"status": "pinned"}

# Start background tasks
async def start_background_tasks():
    # Sync all connectors every 15 minutes
    while True:
        await asyncio.sleep(900)  # 15 minutes
        await gmail_connector.sync()
        await notion_connector.sync()
        await slack_connector.sync()
        await calendar_connector.sync()
        await document_processor.sync()
        await voice_processor.sync()

if __name__ == "__main__":
    import uvicorn
    asyncio.create_task(start_background_tasks())
    uvicorn.run(app, host="127.0.0.1", port=8000)