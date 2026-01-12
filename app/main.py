from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


# ======================================================
# Environment
# ======================================================
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-fastapi-python")

CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "fastapi_rest_snippets")

EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")


# ======================================================
# App
# ======================================================
app = FastAPI(title="FastAPI + Ollama + ChromaDB RAG Demo", version="1.0.0")


# ======================================================
# Embeddings (computed locally in this app)
# ======================================================
embedder = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)


def embed_texts(texts: List[str]) -> List[List[float]]:
    # SentenceTransformerEmbeddingFunction is callable and returns List[List[float]]
    return embedder(texts)


# ======================================================
# ChromaDB (Server mode / HttpClient)
# ======================================================
chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)


def wait_for_chroma(timeout_s: int = 45) -> None:
    """Wait until Chroma's heartbeat endpoint responds."""
    start = time.time()
    url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v1/heartbeat"
    while True:
        try:
            with httpx.Client(timeout=2.0) as client:
                r = client.get(url)
                if r.status_code == 200:
                    return
        except Exception:
            pass

        if time.time() - start > timeout_s:
            raise RuntimeError(f"ChromaDB not ready after {timeout_s}s: {url}")
        time.sleep(1)


# IMPORTANT FIX:
# - Do NOT pass embedding_function to get_or_create_collection when using HttpClient
# - Compute embeddings here and pass embeddings explicitly to add/query
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)


# ======================================================
# Seed Data (expanded)
# ======================================================
SAMPLE_SNIPPETS: List[Dict[str, str]] = [
    {
        "id": "health_check",
        "title": "GET /health simple health check",
        "text": """from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
""",
    },
    {
        "id": "get_items_paginated",
        "title": "GET /items with pagination and filters",
        "text": """from typing import List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    category: Optional[str] = None

@app.get("/items", response_model=List[Item])
async def list_items(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None
) -> List[Item]:
    data = [
        Item(id=1, name="Widget", category="tools"),
        Item(id=2, name="Gadget", category="electronics"),
    ]
    if category:
        data = [i for i in data if i.category == category]
    return data[offset : offset + limit]
""",
    },
    {
        "id": "post_create_item",
        "title": "POST /items create with validation",
        "text": """from fastapi import FastAPI, status
from pydantic import BaseModel, Field

app = FastAPI()

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)

class ItemOut(BaseModel):
    id: int
    name: str
    price: float

@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemCreate) -> ItemOut:
    return ItemOut(id=1, name=payload.name, price=payload.price)
""",
    },
    {
        "id": "put_update_item",
        "title": "PUT /items/{id} update endpoint",
        "text": """from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class ItemUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

@app.put("/items/{item_id}")
async def update_item(item_id: int, payload: ItemUpdate) -> dict[str, str]:
    if item_id != 1:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item updated"}
""",
    },
    {
        "id": "delete_item",
        "title": "DELETE /items/{id} endpoint",
        "text": """from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> None:
    if item_id != 1:
        raise HTTPException(status_code=404, detail="Item not found")
    return None
""",
    },
    {
        "id": "router_example",
        "title": "FastAPI APIRouter best practice",
        "text": """from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

class UserOut(BaseModel):
    id: int
    email: str

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int) -> UserOut:
    return UserOut(id=user_id, email="user@example.com")
""",
    },
    {
        "id": "dependency_example",
        "title": "FastAPI dependency injection",
        "text": """from fastapi import Depends, FastAPI

app = FastAPI()

def get_current_user() -> str:
    return "admin"

@app.get("/secure")
async def secure_endpoint(user: str = Depends(get_current_user)) -> dict[str, str]:
    return {"user": user}
""",
    },
]


# ======================================================
# Seed Logic (explicit embeddings for server mode)
# ======================================================
def seed_if_empty() -> Dict[str, Any]:
    existing = collection.count()
    if existing > 0:
        return {"seeded": False, "count": existing}

    docs = [s["text"] for s in SAMPLE_SNIPPETS]
    embs = embed_texts(docs)

    collection.add(
        ids=[s["id"] for s in SAMPLE_SNIPPETS],
        documents=docs,
        metadatas=[{"title": s["title"]} for s in SAMPLE_SNIPPETS],
        embeddings=embs,
    )
    return {"seeded": True, "count": collection.count()}


# ======================================================
# API Models
# ======================================================
class SeedResponse(BaseModel):
    seeded: bool
    count: int


class QueryRequest(BaseModel):
    query: str = Field(min_length=3)
    n_results: int = Field(3, ge=1, le=10)


class Match(BaseModel):
    id: str
    title: Optional[str]
    score: float
    code: str


class QueryResponse(BaseModel):
    query: str
    matches: List[Match]


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=10)
    use_context: bool = True
    n_context: int = Field(2, ge=0, le=5)


class GenerateResponse(BaseModel):
    model: str
    code: str


# ======================================================
# Startup
# ======================================================
@app.on_event("startup")
def startup() -> None:
    wait_for_chroma()
    seed_if_empty()


# ======================================================
# Routes
# ======================================================
@app.post("/seed", response_model=SeedResponse)
def seed() -> SeedResponse:
    return SeedResponse(**seed_if_empty())


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    q_emb = embed_texts([req.query])[0]

    res = collection.query(
        query_embeddings=[q_emb],
        n_results=req.n_results,
        include=["documents", "metadatas", "distances"],
    )

    ids = res["ids"][0]
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]

    matches: List[Match] = []
    for _id, doc, meta, dist in zip(ids, docs, metas, dists):
        # cosine distance -> higher score is better
        score = 1.0 / (1.0 + float(dist))
        matches.append(
            Match(
                id=str(_id),
                title=(meta or {}).get("title"),
                score=score,
                code=str(doc),
            )
        )

    return QueryResponse(query=req.query, matches=matches)


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest) -> GenerateResponse:
    context = ""

    if req.use_context and req.n_context > 0:
        q_emb = embed_texts([req.prompt])[0]
        ctx = collection.query(
            query_embeddings=[q_emb],
            n_results=req.n_context,
            include=["documents", "metadatas"],
        )

        blocks: List[str] = []
        for doc, meta in zip(ctx["documents"][0], ctx["metadatas"][0]):
            title = (meta or {}).get("title") or "snippet"
            blocks.append(f"# CONTEXT: {title}\n{doc}")

        context = "\n\n".join(blocks)

    prompt = f"{context}\n\n# TASK:\n{req.prompt}\n" if context else req.prompt

    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        r.raise_for_status()
        data = r.json()

    return GenerateResponse(model=OLLAMA_MODEL, code=(data.get("response") or "").strip())
