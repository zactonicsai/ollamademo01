# ollamademo01
# Ollama + FastAPI + ChromaDB Demo Tutorial

## Overview

This tutorial explains the concepts and architecture behind the **Ollama + FastAPI + ChromaDB** demo you just downloaded. The goal of this stack is to show how to:

* Run a **local LLM** using Ollama
* Create a **custom, constrained coding model** (Python + FastAPI only)
* Store and search **typed REST API code snippets** using ChromaDB
* Combine retrieval (RAG) + generation for backend development workflows

This pattern is ideal for:

* Offline / local AI development
* Secure environments
* Developer copilots
* API scaffolding assistants

---

## Architecture at a Glance

```
User / Client
   |
   v
FastAPI App (RAG + Embedder)
   |        \
   |         \--> Ollama (LLM Generation)
   |
   \--> ChromaDB (Vector Search)
```

### Containers

* **Ollama** – runs the LLM locally
* **ChromaDB** – vector database for embeddings
* **FastAPI app** – orchestrates embeddings, search, and generation

All services are wired together via **Docker Compose**.

---

## Core Concepts

### 1. Ollama (Local LLM Runtime)

Ollama allows you to:

* Run LLMs locally (no cloud dependency)
* Pull community or official models
* Create **custom models** using a `Modelfile`

In this demo:

* Base model: `dagbs/qwen2.5-coder-1.5b-instruct-abliterated`
* Custom model: `qwen2.5-fastapi-python`

The custom model enforces **strict output rules**:

* Python only
* FastAPI only
* Typed endpoints
* No markdown or explanations

This is critical for **tooling and automation**, where free-form text is undesirable.

#### Key Files

* `ollama/Modelfile`
* `ollama/init-ollama.sh`

The model is created automatically at container startup.

---

### 2. Modelfile (Behavior Shaping)

A `Modelfile` is similar to a Dockerfile for models.

Key elements used:

* `FROM` – base model
* `PARAMETER` – inference controls (temperature, context)
* `SYSTEM` – hard behavioral rules

This demo uses a **low temperature** to reduce hallucinations and enforce consistency.

---

### 3. FastAPI (Typed API Layer)

FastAPI provides:

* Async-first Python APIs
* Pydantic models for validation
* Automatic OpenAPI schemas

In this demo, FastAPI acts as:

* A **RAG orchestrator**
* An embedding service
* A query + generation API

Endpoints include:

* `/seed` – load example code snippets
* `/query` – semantic search over snippets
* `/generate` – RAG-enhanced code generation

---

### 4. ChromaDB (Vector Database)

ChromaDB stores embeddings for:

* FastAPI GET examples
* FastAPI POST examples
* Typed request/response models

Key ideas:

* Text → Embedding → Vector
* Similar vectors ≈ similar meaning

The demo uses:

* SentenceTransformers embeddings
* Cosine similarity

Chroma enables:

* Code search
* Context injection (RAG)
* Pattern reuse

---

### 5. Embeddings

Embeddings convert text into numeric vectors.

In this stack:

* Model: `all-MiniLM-L6-v2`
* Used for both indexing and querying

Embeddings allow queries like:

> "typed fastapi post endpoint"

To match code examples **without keyword matching**.

---

### 6. Retrieval-Augmented Generation (RAG)

RAG combines:

1. **Retrieve** relevant snippets from Chroma
2. **Augment** the LLM prompt with those snippets
3. **Generate** new code with grounded context

Benefits:

* Less hallucination
* More consistent patterns
* Reuse of proven code styles

In this demo, RAG is optional and configurable per request.

---

## Docker Compose Breakdown

### Why Docker Compose?

* Reproducibility
* Local-first development
* Clear service boundaries

Services:

* `ollama` – LLM runtime
* `chroma` – vector DB
* `app` – FastAPI embedder

Volumes are used to persist:

* Models
* Vector data

---

## Typical Developer Workflow

1. Start stack

   ```bash
   docker compose up --build
   ```

2. Seed examples

   ```bash
   POST /seed
   ```

3. Search patterns

   ```bash
   POST /query
   ```

4. Generate new API code

   ```bash
   POST /generate
   ```

5. Copy generated Python code directly into your project

---

## Why This Pattern Is Powerful

* Works **offline**
* Deterministic output
* No vendor lock-in
* Ideal for regulated environments
* Easy to extend (auth, DBs, routers)

Common extensions:

* SQLModel / SQLAlchemy snippets
* Auth + OAuth patterns
* Dependency injection templates
* Test generation

---

## Official Documentation Links

### Ollama

* [https://ollama.com](https://ollama.com)
* [https://ollama.com/library](https://ollama.com/library)
* [https://github.com/ollama/ollama](https://github.com/ollama/ollama)
* [https://github.com/ollama/ollama/blob/main/docs/modelfile.md](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)

### ChromaDB

* [https://www.trychroma.com](https://www.trychroma.com)
* [https://docs.trychroma.com](https://docs.trychroma.com)
* [https://github.com/chroma-core/chroma](https://github.com/chroma-core/chroma)

### FastAPI

* [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
* [https://fastapi.tiangolo.com/tutorial/](https://fastapi.tiangolo.com/tutorial/)

### Sentence Transformers

* [https://www.sbert.net](https://www.sbert.net)

---

## Research Papers & References

### Retrieval-Augmented Generation

* Lewis et al. (2020) – *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*

### Vector Search

* Johnson et al. – *Billion-scale similarity search with FAISS*

### Embeddings

* Reimers & Gurevych – *Sentence-BERT*

---

## When to Use This Stack

Use this architecture when you need:

* Secure AI-assisted coding
* Repeatable API scaffolding
* Internal developer tools
* Knowledge-aware code generation

Avoid it when:

* You need very large models
* Latency must be <10ms
* Cloud-only compliance is required

---

## Next Steps

Suggested enhancements:

* Add `APIRouter` conventions
* Enforce project layout generation
* Add unit test generation
* Store OpenAPI specs as embeddings

---

## Summary

This demo shows how modern backend development can be accelerated by:

* Local LLMs (Ollama)
* Semantic memory (ChromaDB)
* Typed APIs (FastAPI)

Together, they form a **local, deterministic, developer copilot**.

---

## Hands-On Lab (cURL & Postman)

This lab walks you through running the stack, seeding data, querying ChromaDB, and generating FastAPI code using Ollama.

---

### Prerequisites

* Docker + Docker Compose
* curl
* (Optional) Postman Desktop

---

### Step 1: Start the Stack

```bash
docker compose up --build
```

Wait until you see logs indicating:

* Ollama is serving on `11434`
* Model `qwen2.5-fastapi-python` is created
* FastAPI app is running on `9000`

---

### Step 2: Seed Example Snippets

The app auto-seeds on startup, but you can force it.

#### cURL

```bash
curl -X POST http://localhost:9000/seed
```

Expected response:

```json
{
  "seeded": true,
  "count": 4
}
```

#### Postman

* Method: **POST**
* URL: `http://localhost:9000/seed`
* Body: *(empty)*

---

### Step 3: Semantic Query (Vector Search)

Search for similar FastAPI patterns.

#### cURL

```bash
curl -X POST http://localhost:9000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "typed fastapi post endpoint with pydantic model",
    "n_results": 3
  }'
```

#### Postman

* Method: **POST**
* URL: `http://localhost:9000/query`
* Headers: `Content-Type: application/json`
* Body (raw JSON):

```json
{
  "query": "typed fastapi post endpoint with pydantic model",
  "n_results": 3
}
```

You should see matching code snippets returned from ChromaDB.

---

### Step 4: Generate Code with RAG

This step combines Chroma retrieval + Ollama generation.

#### cURL

```bash
curl -X POST http://localhost:9000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a FastAPI router with GET /health and POST /items using typed Pydantic models",
    "use_context": true,
    "n_context": 2
  }'
```

#### Postman

* Method: **POST**
* URL: `http://localhost:9000/generate`
* Headers: `Content-Type: application/json`
* Body (raw JSON):

```json
{
  "prompt": "Create a FastAPI router with GET /health and POST /items using typed Pydantic models",
  "use_context": true,
  "n_context": 2
}
```

The response will contain **Python-only FastAPI code** with no markdown.

---

### Step 5: Validate Output

* Paste generated code into a local FastAPI project
* Run `uvicorn main:app --reload`
* Verify endpoints via browser or Swagger UI

---

## GitHub README.md (Template)

# Ollama + FastAPI + ChromaDB (Local RAG Demo)

A local, Docker-based demo showing how to combine **Ollama**, **FastAPI**, and **ChromaDB** to build a deterministic, Python-only FastAPI code generator using Retrieval-Augmented Generation (RAG).

## Features

- Local LLM execution (no cloud dependency)
- Custom Ollama model constrained to Python + FastAPI
- Vector search over typed REST API examples
- RAG-based code generation
- Docker Compose setup

## Architecture

- Ollama – LLM runtime
- ChromaDB – vector database
- FastAPI – orchestration layer

## Requirements

- Docker
- Docker Compose

## Quick Start

```bash
docker compose up --build
````

FastAPI will be available at:

* [http://localhost:9000](http://localhost:9000)

## API Endpoints

* `POST /seed` – load example snippets
* `POST /query` – semantic search
* `POST /generate` – RAG-based code generation

## Example

```bash
curl -X POST http://localhost:9000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Create a typed FastAPI POST endpoint"}'
```

## Why This Exists

This project demonstrates how to build:

* Offline developer copilots
* Secure AI tooling
* Deterministic code generation pipelines

## Docs

* Ollama: [https://ollama.com](https://ollama.com)
* ChromaDB: [https://docs.trychroma.com](https://docs.trychroma.com)
* FastAPI: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

## License

MIT
