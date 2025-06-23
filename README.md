# mem0_service

A simple MCP-compatible memory server providing long term storage for AI agents.
It exposes three tools over the Model Context Protocol and can run over SSE or
stdio transport.

## Features
- Store memories with embeddings in PostgreSQL (pgvector) or in-memory
- Semantic search using cosine similarity
- Works with OpenAI, OpenRouter or Ollama for embeddings
- Health check at `/health`

## Quick start
1. Copy `.env.example` to `.env` and adjust values.
2. Run with Docker Compose:
   ```bash
   docker compose up
   ```
   You should see `🚀 Server listening on http://0.0.0.0:8050`.

### Curl test
Save a memory then search for it:
```bash
curl -X POST http://localhost:8050/save_memory \
     -H "Content-Type: application/json" \
     -d '{"text":"Craig closed $2M in premiums"}'

curl -X POST http://localhost:8050/search_memories \
     -H "Content-Type: application/json" \
     -d '{"query":"premiums"}'
```

### Stdio example
Set `TRANSPORT=stdio` in `.env` and run:
```bash
python -m src.main
```
A compatible client can then communicate with the process via stdin/stdout.
