import re
from sentence_transformers import SentenceTransformer

# Load local embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')


def chunk_text(text, max_tokens=500, overlap_tokens=50):
    # Split on semantic boundaries (paragraphs)
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
        
        # Add paragraph to current chunk
        if len(current_chunk) > 0:
            test_chunk = f"{current_chunk} {paragraph}"
        else:
            test_chunk = paragraph
        
        # If adding this paragraph would exceed max_tokens, save current chunk
        if len(model.encode(test_chunk)) > max_tokens:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk = test_chunk
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Apply overlap between chunks
    overlapped_chunks = []
    for i, chunk in enumerate(chunks):
        if i > 0:
            prev_chunk = chunks[i-1]
            # Extract last sentence of previous chunk to add as context
            sentences = re.split(r'[.!?]+', prev_chunk)
            if len(sentences) > 1:
                context_prefix = sentences[-2] + ". "
                overlapped_chunks.append(context_prefix + chunk)
            else:
                overlapped_chunks.append(chunk)
        else:
            overlapped_chunks.append(chunk)
    
    return overlapped_chunks