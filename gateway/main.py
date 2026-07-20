"""Small authenticated OpenAI-compatible proxy for one llama.cpp backend."""
import os

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, StreamingResponse

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_KEY = os.getenv("API_KEY", "")
client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=httpx.Timeout(300, connect=30))
app = FastAPI(title="AMD APU Vulkan Gateway")

def authorize(request: Request) -> None:
    if API_KEY and request.headers.get("Authorization") != f"Bearer {API_KEY}":
        raise HTTPException(401, "Invalid or missing API key")

@app.on_event("shutdown")
async def close_client() -> None:
    await client.aclose()

@app.get("/health")
async def health():
    try:
        response = await client.get("/health")
        return {"status": "ok" if response.is_success else "degraded", "backend_status": response.status_code}
    except httpx.HTTPError:
        return {"status": "degraded", "backend_status": "unreachable"}

@app.get("/v1/models")
async def models(request: Request):
    authorize(request)
    response = await client.get("/v1/models")
    response.raise_for_status()
    data = response.json()
    for model in data.get("data", []): model["id"] = "gpu-" + model["id"]
    return data

@app.post("/v1/chat/completions")
async def chat(request: Request):
    authorize(request)
    body = await request.json()
    model = body.get("model", "")
    if model.startswith("gpu-"): body["model"] = model[4:]
    stream = bool(body.get("stream"))
    if stream:
        async def relay():
            async with client.stream("POST", "/v1/chat/completions", json=body) as response:
                async for chunk in response.aiter_raw():
                    yield chunk
        return StreamingResponse(relay(), media_type="text/event-stream")
    response = await client.post("/v1/chat/completions", json=body)
    return Response(response.content, status_code=response.status_code,
                    media_type=response.headers.get("content-type"))
