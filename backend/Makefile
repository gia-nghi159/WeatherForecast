.PHONY: setup run test warm clean docker-build docker-run

# Install dependencies using uv
setup:
	uv sync

# Run the FastAPI server locally
run:
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run Locust load testing
test:
	uv run locust -f locustfile.py --host http://localhost:8000

# Execute cache warming
warm:
	uv run python -m src.warm_cache

# Build and run Docker container locally
docker-build:
	docker build -t weather-backend:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env weather-backend:latest

# Clean up temporary Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete