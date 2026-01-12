#!/bin/sh
set -eu

echo "==> Starting Ollama init..."

# Wait for Ollama HTTP server to come up
OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"

echo "==> Waiting for Ollama API at ${OLLAMA_HOST} ..."
i=0
until wget -qO- "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; do
  i=$((i+1))
  if [ "$i" -ge 60 ]; then
    echo "ERROR: Ollama API did not become ready in time."
    exit 1
  fi
  sleep 1
done

echo "==> Pulling base model..."
ollama pull dagbs/qwen2.5-coder-1.5b-instruct-abliterated

echo "==> Creating custom model qwen2.5-fastapi-python ..."
ollama create qwen2.5-fastapi-python -f /models/Modelfile || true

echo "==> Done. Models:"
ollama list
