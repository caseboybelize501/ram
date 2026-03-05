import os
from faster_whisper import WhisperModel
from src.ingestion.chunker import chunk_text
from src.storage.chroma_store import ChromaStore
from src.ingestion.entity_extractor import extract_entities


class VoiceProcessor:
    def __init__(self):
        self.model = None
        self.chroma_store = ChromaStore()
        self._load_model()

    def _load_model(self):
        # Load local whisper model
        self.model = WhisperModel("small", device="cpu", compute_type="int8")

    async def sync(self):
        try:
            audio_dir = os.path.expanduser('~/.personalai/voice_memos')
            if not os.path.exists(audio_dir):
                return
            
            for filename in os.listdir(audio_dir):
                file_path = os.path.join(audio_dir, filename)
                if filename.endswith(('.mp3', '.wav', '.m4a')):
                    await self._process_audio(file_path)
        except Exception as e:
            print(f"Error processing voice memos: {e}")

    async def _process_audio(self, file_path):
        segments, info = self.model.transcribe(file_path, beam_size=5)
        text = " ".join([segment.text for segment in segments])
        
        chunks = chunk_text(text)
        entities = extract_entities(text)
        
        for i, chunk in enumerate(chunks):
            self.chroma_store.add_chunk({
                "text": chunk,
                "source": "voice_memo",
                "source_url": file_path,
                "date": os.path.getctime(file_path),
                "entities": entities
            })

    def get_status(self):
        return {"status": "active"}