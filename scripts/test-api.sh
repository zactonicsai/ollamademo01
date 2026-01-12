#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE:-http://localhost:9000}"

echo "======================================================"
echo "FastAPI Embedder API Smoke Tests"
echo "API_BASE = ${API_BASE}"
echo "======================================================"
echo

echo "1) POST /seed"
curl -sS -X POST "${API_BASE}/seed"
echo
echo

echo "2) POST /query (semantic search)"
curl -sS -X POST "${API_BASE}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "typed fastapi post endpoint with pydantic request model",
    "n_results": 3
  }'
echo
echo

echo "3) POST /generate (RAG on)"
curl -sS -X POST "${API_BASE}/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a FastAPI router with GET /health and POST /items using typed Pydantic models.",
    "use_context": true,
    "n_context": 2
  }'
echo
echo

echo "Done ✅"
