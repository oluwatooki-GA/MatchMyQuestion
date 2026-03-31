#!/bin/bash
set -e

echo "Downloading model..."
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2', device='cpu')"
echo "Model downloaded."

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT