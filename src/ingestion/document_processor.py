import os
from PyPDF2 import PdfReader
from docx import Document
from src.ingestion.chunker import chunk_text
from src.storage.chroma_store import ChromaStore
from src.ingestion.entity_extractor import extract_entities


class DocumentProcessor:
    def __init__(self):
        self.chroma_store = ChromaStore()

    async def sync(self):
        try:
            # Process all PDFs and DOCX files in documents directory
            docs_dir = os.path.expanduser('~/.personalai/documents')
            if not os.path.exists(docs_dir):
                return
            
            for filename in os.listdir(docs_dir):
                file_path = os.path.join(docs_dir, filename)
                if filename.endswith('.pdf'):
                    await self._process_pdf(file_path)
                elif filename.endswith('.docx'):
                    await self._process_docx(file_path)
        except Exception as e:
            print(f"Error processing documents: {e}")

    async def _process_pdf(self, file_path):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        chunks = chunk_text(text)
        entities = extract_entities(text)
        
        for i, chunk in enumerate(chunks):
            self.chroma_store.add_chunk({
                "text": chunk,
                "source": "document",
                "source_url": file_path,
                "date": os.path.getctime(file_path),
                "entities": entities
            })

    async def _process_docx(self, file_path):
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        chunks = chunk_text(text)
        entities = extract_entities(text)
        
        for i, chunk in enumerate(chunks):
            self.chroma_store.add_chunk({
                "text": chunk,
                "source": "document",
                "source_url": file_path,
                "date": os.path.getctime(file_path),
                "entities": entities
            })

    def get_status(self):
        return {"status": "active"}