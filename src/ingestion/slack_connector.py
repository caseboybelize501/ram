import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.ingestion.chunker import chunk_text
from src.storage.chroma_store import ChromaStore
from src.ingestion.entity_extractor import extract_entities


class SlackConnector:
    def __init__(self):
        self.client = None
        self.chroma_store = ChromaStore()
        self._authenticate()

    def _authenticate(self):
        token = os.getenv('SLACK_TOKEN')
        if not token:
            raise Exception("SLACK_TOKEN environment variable required")
        self.client = WebClient(token=token)

    async def sync(self):
        try:
            channels = self.client.conversations_list(types=["public_channel", "private_channel"])
            for channel in channels['channels']:
                await self._process_channel(channel)
        except Exception as e:
            print(f"Error syncing Slack: {e}")

    async def _process_channel(self, channel):
        try:
            messages = self.client.conversations_history(channel=channel['id'])
            for msg in messages['messages']:
                if 'text' in msg:
                    chunks = chunk_text(msg['text'])
                    entities = extract_entities(msg['text'])
                    
                    for i, chunk in enumerate(chunks):
                        self.chroma_store.add_chunk({
                            "text": chunk,
                            "source": "slack",
                            "source_url": f"https://app.slack.com/client/{channel['id']}",
                            "date": msg.get('ts', ''),
                            "entities": entities
                        })
        except SlackApiError as e:
            print(f"Error processing channel {channel['name']}: {e.response['error']}")

    def get_status(self):
        return {"status": "connected" if self.client else "disconnected"}