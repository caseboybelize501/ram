import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from src.ingestion.chunker import chunk_text
from src.storage.chroma_store import ChromaStore
from src.ingestion.entity_extractor import extract_entities


class CalendarConnector:
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    TOKEN_FILE = os.path.expanduser('~/.personalai/calendar_token.pickle')
    CREDENTIALS_FILE = os.path.expanduser('~/.personalai/calendar_credentials.json')

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

        self.service = build('calendar', 'v3', credentials=creds)

    async def sync(self):
        try:
            events = self._fetch_events()
            for event in events:
                await self._process_event(event)
        except Exception as e:
            print(f"Error syncing Calendar: {e}")

    def _fetch_events(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                    maxResults=50, singleEvents=True,
                                                    orderBy='startTime').execute()
        return events_result.get('items', [])

    async def _process_event(self, event):
        summary = event.get('summary', '')
        description = event.get('description', '')
        
        content = f"{summary} {description}"
        chunks = chunk_text(content)
        entities = extract_entities(content)
        
        for i, chunk in enumerate(chunks):
            self.chroma_store.add_chunk({
                "text": chunk,
                "source": "calendar",
                "source_url": event.get('htmlLink', ''),
                "date": event.get('created', ''),
                "entities": entities
            })

    def get_status(self):
        return {"status": "connected" if self.service else "disconnected"}