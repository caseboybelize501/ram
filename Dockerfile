FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install system dependencies for spaCy
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY src/ ./src/
COPY frontend/ ./frontend/

# Download spaCy model
RUN python -m spacy download en_core_web_sm

EXPOSE 8000

CMD ["python", "src/main.py"]