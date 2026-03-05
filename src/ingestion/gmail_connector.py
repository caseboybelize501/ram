import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from src.ingestion.chunker import chunk_text
from src.storage.chroma_store import ChromaStore
from src.ingestion.entity_extractor import extract_entities
import base64

class GmailConnector:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    TOKEN_FILE = os.path.expanduser('~/.personalai/gmail_token.pickle')
    CREDENTIALS_FILE = os.path.expanduser('~/.personalai/gmail_credentials.json')

    def __init__(self):
        self.service = None
        self.chroma_store = ChromaStore()
        self._authenticate()

    def _authenticate(self):
        if not os.path.exists(os.path.dirname(self.TOKEN_FILE)):
            os.makedirs(os.path.dirname(self.TOKEN_FILE))

        creds = None
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    async def sync(self):
        try:
            messages = self._fetch_messages()
            for message in messages:
                await self._process_message(message)
        except Exception as e:
            print(f"Error syncing Gmail: {e}")

    def _fetch_messages(self):
        results = self.service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])
        return messages

    async def _process_message(self, message):
        msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
        
        # Extract text from email
        payload = msg['payload']
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        # Chunk and store
        chunks = chunk_text(body)
        entities = extract_entities(body)
        
        for i, chunk in enumerate(chunks):
            self.chroma_store.add_chunk({
                "text": chunk,
                "source": "gmail",
                "source_url": f"https://mail.google.com/mail/u/0/#inbox/{message['id']}",
                "date": msg.get('internalDate', ''),
                "entities": entities
            })

    def get_status(self):
        return {"status": "connected" if self.service else "disconnected"}