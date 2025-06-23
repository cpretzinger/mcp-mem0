import os
import httpx
from typing import List

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL_CHOICE", "text-embedding-3-small")

async def get_embedding(text: str) -> List[float]:
    headers = {"Authorization": f"Bearer {LLM_API_KEY}"} if LLM_API_KEY else {}
    if LLM_PROVIDER in {"openai", "openrouter"}:
        url = f"{LLM_BASE_URL}/embeddings"
        payload = {"input": text, "model": EMBED_MODEL}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()["data"][0]["embedding"]
    elif LLM_PROVIDER == "ollama":
        url = f"{LLM_BASE_URL}/embeddings"
        payload = {"prompt": text, "model": EMBED_MODEL}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()["embedding"]
    else:
        raise ValueError(f"Unsupported provider {LLM_PROVIDER}")
