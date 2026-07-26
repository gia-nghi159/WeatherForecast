# 🌤️ WeatherForecast: Automated MLOps & K8s Architecture
A full-stack, real-time weather dashboard and 7-day Machine Learning temperature forecast for Dallas, TX. This project showcases a complete end-to-end local microservices architecture, featuring Kubernetes orchestration, Infrastructure as Code (IaC), and automated MLOps pipelines.

---

## ✨ Features

* **Real-Time Telemetry:** Live current conditions (temperature, wind, pressure, precipitation) fetched and cached for performance.
* **ML-Powered 7-Day Forecast:** Daily maximum temperature predictions powered by a custom-trained Lasso Regression model.
* **Responsive UI:** Built with React & TypeScript, featuring dynamic weather icons and instant unit conversions (°C ⇄ °F, km/h ⇄ mph).
* **High-Performance Caching:** Redis integration to cache API responses, reducing ML inference overhead and external API calls.
* **Kubernetes Orchestration:** Backend containerized and deployed on a local Minikube cluster using Helm and Terraform.
* **Automated CI/CD MLOps:** GitHub Actions configured to fetch hourly telemetry, perform daily ground-truth evaluations, and execute weekly model retraining.
* **Load Tested & Autoscaled:** Configured Horizontal Pod Autoscaling (HPA) tested via Locust to handle simulated traffic spikes dynamically.

---

## 🏗️ Tech Stack

### Frontend
* **Core:** React, TypeScript, Vite
* **Styling:** Tailwind CSS / Custom CSS
* **State/Routing:** React Hooks

### Backend & ML
* **Core:** Python, FastAPI, Uvicorn
* **Data Processing:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn (Lasso Regression)
* **Caching:** Redis / FakeRedis (Local Fallback)
* **Package Management:** `uv`

### DevOps & Infrastructure
* **Containerization:** Docker
* **Orchestration:** Kubernetes (Minikube), Helm Charts
* **Infrastructure as Code (IaC):** Terraform
* **CI/CD:** GitHub Actions
* **Testing & Monitoring:** Locust, Pytest, Prometheus, Grafana

---

## 📂 Project Structure

```bash
WeatherForecast/
├── .github/workflows/          # GitHub Actions for automated MLOps cron jobs
│   ├── daily_pipeline.yml
│   ├── hourly_fetch.yml
│   └── weekly_retrain.yml
├── backend/                    # Python FastAPI & ML Pipeline
│   ├── data/                   # Raw CSVs, logs, and Grafana dashboard JSONs
│   ├── models/                 # Serialized ML models (.joblib)
│   ├── notebooks/              # Jupyter notebooks for model exploration
│   ├── src/                    # FastAPI application and ML source code
│   │   ├── config.py           # Environment variables & constants
│   │   ├── main.py             # FastAPI routing and endpoints
│   │   ├── pipeline.py         # Telemetry fetching logic
│   │   ├── preprocessing.py    # Feature engineering for ML
│   │   ├── schemas.py          # Pydantic response models
│   │   └── train.py            # Model training script
│   ├── terraform/              # IaC to provision Kubernetes resources
│   │   └── main.tf
│   ├── tests/                  # Pytest unit tests
│   ├── weather-chart/          # Helm chart for Kubernetes deployment
│   ├── Dockerfile              # Backend container build instructions
│   ├── locustfile.py           # Load testing configuration
│   ├── Makefile                # Automation commands for local setup
│   ├── pyproject.toml          # Python project metadata
│   └── uv.lock                 # Strict dependency locking via uv
└── frontend/                   # React + TypeScript Web App
    ├── public/                 # Static assets
    ├── src/
    │   ├── components/         # Modular React components (Header, ForecastGrid, etc.)
    │   ├── types/              # TypeScript interfaces
    │   ├── utils/              # Helper functions
    │   ├── App.tsx             # Root application component
    │   └── main.tsx            # React DOM entry point
    ├── package.json            # Node dependencies
    └── vite.config.ts          # Vite bundler configuration
```

---

## 💻 Local Development Setup

This project is designed to be run entirely locally. The backend utilizes a `Makefile` to automate the complex orchestration of Docker, Minikube, and Terraform.

### Prerequisites
Make sure you have the following installed on your local machine:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) or OrbStack
* [Minikube](https://minikube.sigs.k8s.io/docs/start/) & `kubectl`
* [Terraform](https://developer.hashicorp.com/terraform/downloads)
* [uv](https://github.com/astral-sh/uv) (Python package manager)
* [Node.js](https://nodejs.org/) & `npm`

### 1. Boot up the Backend (Kubernetes / API)
Navigate to the backend directory and use the Makefile to provision the infrastructure automatically.

```bash
cd backend

# Start Minikube, build the Docker image locally, and install testing dependencies
make setup

# Provision the Kubernetes resources (Helm & Prometheus) via Terraform
make deploy

# Open the network tunnel to expose the local LoadBalancer (requires sudo/admin password)
# NOTE: Leave this terminal window running!
make tunnel
```
*The API is now running locally at: `http://localhost:8000`*

### 2. Start the Frontend (React UI)
Open a **new** terminal window, navigate to the frontend directory, and start the Vite development server.

```bash
cd frontend

# Install Node dependencies
npm install

# Start the frontend dev server
npm run dev
```
*The Web UI is now accessible at: `http://localhost:5173` (or the port Vite provides).*

### 3. Optional: Run Load Tests
To verify Horizontal Pod Autoscaling (HPA) and test the backend's resilience, you can trigger a local swarm test using Locust.

```bash
cd backend
make test
```
*Navigate to `http://localhost:8089` in your browser to start the swarm and monitor response times.*

### 4. Teardown
When you are finished developing, gracefully destroy the infrastructure to free up your system's RAM.

```bash
cd backend
make clean
```