import os
import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from mcp_sdk.server import MCPServer, Context
from dotenv import load_dotenv

from db import init_db, save_memory, search_memories, get_all_memories
from llm import get_embedding

load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8050"))
TRANSPORT = os.getenv("TRANSPORT", "sse")

logging.basicConfig(level=logging.INFO, format='{"timestamp":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}')
logger = logging.getLogger(__name__)

app = FastAPI()

mcp = MCPServer("mem0_service", app=app)

@app.on_event("startup")
async def startup() -> None:
    init_db()
    logger.info("service started")

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

@mcp.tool()
async def save_memory_tool(ctx: Context, text: str) -> str:
    emb = await get_embedding(text)
    mem_id = save_memory(text, emb)
    return mem_id

@mcp.tool()
async def search_memories_tool(ctx: Context, query: str, limit: int = 5) -> str:
    emb = await get_embedding(query)
    results = search_memories(emb, limit)
    return "\n".join(results)

@mcp.tool()
async def get_all_memories_tool(ctx: Context) -> str:
    return "\n".join(get_all_memories())

@app.post("/save_memory")
async def api_save(req: Request):
    data = await req.json()
    emb = await get_embedding(data.get("text", ""))
    mem_id = save_memory(data.get("text", ""), emb)
    return {"id": mem_id}

@app.post("/search_memories")
async def api_search(req: Request):
    data = await req.json()
    emb = await get_embedding(data.get("query", ""))
    results = search_memories(emb, data.get("limit", 5))
    return {"results": results}

@app.get("/get_all_memories")
async def api_get_all():
    return {"results": get_all_memories()}

@app.get("/sse")
async def sse_endpoint(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            await asyncio.sleep(1)
            yield f"data: ping\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def main():
    if TRANSPORT == "stdio":
        await mcp.run_stdio_async()
    else:
        import uvicorn
        config = uvicorn.Config(app, host=HOST, port=PORT, log_level="info")
        server = uvicorn.Server(config)
        logger.info(f"\ud83d\ude80 Server listening on http://{HOST}:{PORT}")
        await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
