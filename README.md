# RAM - Personal AI Memory Operating System

"The AI that knows everything you've ever thought, said, or decided"

## Overview

RAM is a local-first personal AI memory system that continuously ingests from connected sources (Gmail, Notion, Slack, calendar, browser bookmarks, voice memos, uploaded documents) and synthesizes them into a queryable knowledge graph. Users interact with their memory through a conversational interface.

## Features

- **Continuous Ingestion**: Syncs from 15+ tools including Gmail, Notion, Slack, Calendar, Browser History, Voice Memos, Documents
- **Local-First Architecture**: All processing happens locally - no data leaves your machine
- **Knowledge Graph**: Links related concepts, people, decisions, and projects
- **Hybrid Retrieval**: Combines vector similarity search with graph traversal and temporal ranking
- **Privacy First**: Zero external API calls for AI or embeddings
- **Proactive Surface Engine**: Triggers memory recall when relevant context is detected

## Architecture


┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  Data Sources │───▶│ Ingestion Pipeline │───▶│ Storage Layer │
└─────────────┘    └──────────────┘    └──────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │ Hybrid Retriever │
                    └──────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │ Answer Generator │
                    └──────────────┘


## Data Sources

- Gmail → emails, threads, attachments
- Notion → pages, databases
- Slack → messages, threads, DMs
- Calendar → events, attendees, notes
- Browser → bookmarks, reading history (extension)
- Voice memos → audio → Whisper transcription
- Documents → PDF/DOCX → text extraction

## Storage Layer

- ChromaDB (vector store)
- Neo4j (knowledge graph overlay)

## Retrieval Pipeline

1. Query embedding
2. Vector similarity search (ChromaDB)
3. Graph traversal (Neo4j)
4. Temporal ranking
5. Cross-encoder reranking
6. Hybrid retrieval

## Privacy Architecture

- All processing local
- OAuth tokens stored in encrypted SQLite
- Data stored in ~/.personalai with 0700 permissions
- Connectors pull-only, no writing back to source systems

## Sync Frequency

Configurable per source (default: every 15 minutes)

## Installation

bash
# Clone the repository
# Set up environment variables
# Run with Docker Compose


## Usage

1. Connect your accounts via OAuth
2. Start the application
3. Ask questions in natural language
4. Receive grounded answers with citations

## API Endpoints

- `POST /api/query` → Query memory
- `GET /api/sync/status` → Get sync status
- `POST /api/sync/trigger` → Force sync
- `GET /api/graph/entities` → Get top entities
- `GET /api/timeline` → Chronological memory feed
- `POST /api/memory/pin` → Pin important memory
- `GET /health` → Health check

## License

MIT