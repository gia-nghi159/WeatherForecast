.PHONY: help up down restart logs ps deploy warm test setup run clean

# Default target: display help
help:
	@echo "Available commands:"
	@echo "  make up        - Build and run the entire container stack in background (FastAPI, Redis, Prometheus, Grafana)"
	@echo "  make down      - Stop and remove all containers"
	@echo "  make restart   - Rebuild and restart all containers"
	@echo "  make logs      - Tail logs from all containers (or specific: make logs c=backend)"
	@echo "  make ps        - Check status of all containers"
	@echo "  make warm      - Warm the Redis cache with sample requests"
	@echo "  make test      - Run Locust load testing against http://localhost:8000"
	@echo "  make setup     - Install local Python dependencies via uv"
	@echo "  make run       - Run FastAPI server locally for development"
	@echo "  make clean     - Clean temporary Python bytecode and artifacts"

# ------------------------------------------------------------------------------
# Container Lifecycle (Docker Compose Stack)
# ------------------------------------------------------------------------------

# Build and start all services in the background
up:
	docker compose up -d --build

# Alias for up
deploy: up

# Stop and remove all running containers and networks
down:
	docker compose down

# Rebuild and restart the stack
restart:
	docker compose down
	docker compose up -d --build

# Stream live container logs (usage: 'make logs' or 'make logs c=backend')
logs:
	docker compose logs -f $(c)

# Display status of containers and exposed ports
ps:
	docker compose ps

# ------------------------------------------------------------------------------
# Local Development & Testing
# ------------------------------------------------------------------------------

# Install local dependencies
setup:
	uv sync

# Run FastAPI server locally with auto-reload
run:
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Execute cache warming against the running API
warm:
	uv run python -m src.warm_cache

# Run Locust load testing
test:
	uv run locust -f locustfile.py --host http://127.0.0.1:8000

# Clean up Python cache and temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete