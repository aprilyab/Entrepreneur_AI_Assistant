.PHONY: help setup build up down restart ps logs health backend-shell frontend-shell \
	check check-backend check-frontend smoke smoke-full clean

help:
	@echo "Prooflane development commands"
	@echo "  make setup           Copy env template if needed and start the stack"
	@echo "  make build           Build production Docker images"
	@echo "  make up              Start PostgreSQL, FastAPI, and Next.js"
	@echo "  make down            Stop the stack (database volume is preserved)"
	@echo "  make restart         Rebuild and restart the stack"
	@echo "  make ps              Show service status"
	@echo "  make logs            Follow service logs"
	@echo "  make health          Check frontend and backend over HTTP"
	@echo "  make check           Run deterministic backend checks and frontend build"
	@echo "  make smoke           Exercise authenticated validation CRUD"
	@echo "  make smoke-full      Run a live end-to-end AI generation (uses API quota)"
	@echo "  make clean           Remove generated local caches only"

setup:
	./setup.sh

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose up -d --build

ps:
	docker compose ps

logs:
	docker compose logs -f

health:
	curl --fail --silent http://localhost:8000/health
	@echo
	curl --fail --silent --output /dev/null http://localhost:3000
	@echo "Frontend healthy"

backend-shell:
	docker compose exec backend /bin/sh

frontend-shell:
	docker compose exec frontend /bin/sh

check: check-backend check-frontend

check-backend:
	docker compose exec -T backend python scripts/check_deterministic.py
	docker compose exec -T backend python scripts/check_exports.py

check-frontend:
	docker compose exec -T frontend npm run build

smoke:
	docker compose exec -T backend python scripts/smoke_validation_workspace.py

smoke-full:
	docker compose exec -T backend python scripts/smoke_full_generation.py

clean:
	find backend frontend -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf frontend/.next frontend/tsconfig.tsbuildinfo
	@echo "Removed generated caches. Dependencies and PostgreSQL data were preserved."
