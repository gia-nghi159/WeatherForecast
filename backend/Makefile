# Makefile

.PHONY: setup deploy test clean

# 1. Boots the cluster and builds the local Docker image
setup:
	@echo "Starting Minikube..."
	minikube start --memory=6144 --cpus=4
	@echo "Building Docker image inside Minikube..."
	minikube image build -t weather-backend:latest .
	@echo "Installing local Python dependencies for testing..."
	uv sync

# 2. Applies the Terraform infrastructure
deploy:
	@echo "Provisioning infrastructure with Terraform..."
	terraform init
	terraform apply -auto-approve
	@echo "Deployment complete! Run 'make tunnel' in a new window."

# 3. Opens the tunnel (Needs its own terminal window)
tunnel:
	@echo "Opening Minikube tunnel (requires sudo password)..."
	sudo minikube tunnel

# 4. Runs the Locust load test
test:
	@echo "Starting Locust load test..."
	uv run locust -f locustfile.py

# 5. Streams the live logs from the FastAPI pods
logs:
	@echo "Streaming backend logs (Press Ctrl+C to stop)..."
	kubectl logs -f -l app=weather-backend

# 6. Tears everything down to free up RAM
clean:
	@echo "Destroying infrastructure and stopping Minikube..."
	terraform destroy -auto-approve
	minikube stop