#!/bin/sh
set -e
ollama pull dagbs/qwen2.5-coder-1.5b-instruct-abliterated
ollama create qwen2.5-fastapi-python -f /models/Modelfile
