import os
from notion_client import Client
from src.ingestion.chunker import chunk_text
from src.storage.chroma_store import ChromaStore
from src.ingestion.entity_extractor import extract_entities


class NotionConnector:
    def __init__(self):
        self.client = None
        self.chroma_store = ChromaStore()
        self._authenticate()

    def _authenticate(self):
        token = os.getenv('NOTION_TOKEN')
        if not token:
            raise Exception("NOTION_TOKEN environment variable required")
        self.client = Client(auth=token)

    async def sync(self):
        try:
            databases = self.client.databases.list()
            for db in databases['results']:
                await self._process_database(db)
        except Exception as e:
            print(f"Error syncing Notion: {e}")

    async def _process_database(self, database):
        pages = self.client.databases.query(database_id=database['id'])
        for page in pages['results']:
            await self._process_page(page)

    async def _process_page(self, page):
        # Get page content
        content = ""
        for block in self.client.blocks.children.list(block_id=page['id'])['results']:
            if 'text' in block['paragraph']:
                content += block['paragraph']['text']['content'] + "\n"

        chunks = chunk_text(content)
        entities = extract_entities(content)
        
        for i, chunk in enumerate(chunks):
            self.chroma_store.add_chunk({
                "text": chunk,
                "source": "notion",
                "source_url": page['url'],
                "date": page['created_time'],
                "entities": entities
            })

    def get_status(self):
        return {"status": "connected" if self.client else "disconnected"}