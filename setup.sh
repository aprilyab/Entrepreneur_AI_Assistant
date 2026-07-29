#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required. Install Docker Engine or Docker Desktop first."
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "The Docker Compose plugin is required."
    exit 1
fi

if [ ! -f .env.local ]; then
    cp .env.example .env.local
    echo "Created .env.local from .env.example. Add a valid GEMINI_API_KEY, then rerun ./setup.sh."
    exit 1
fi

if { ! grep -Eq '^GEMINI_API_KEY=.+$' .env.local || grep -Eq '^GEMINI_API_KEY=(your_|replace_)' .env.local; } \
    && ! grep -Eq '^GEMINI_API_KEYS=\[[^]]+\]$' .env.local; then
    echo "Add a valid GEMINI_API_KEY or GEMINI_API_KEYS list to .env.local before starting the application."
    exit 1
fi

docker compose up --build -d
docker compose ps

echo
echo "Prooflane is running:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
echo
echo "Stop it with: docker compose down"
