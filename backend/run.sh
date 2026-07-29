#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "🚀 Starting Prooflane..."
echo "📊 Backend starting on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
