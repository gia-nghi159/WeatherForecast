# 🌤️ WeatherForecast: Automated MLOps & K8s Architecture

![Weather UI Dashboard](./assets/UI.png)

A full-stack, real-time weather dashboard and 7-day Machine Learning temperature forecast for Dallas, TX. This project showcases a complete end-to-end local microservices architecture, featuring Kubernetes orchestration, Infrastructure as Code (IaC), and automated continuous training (CT) pipelines.

---

## ✨ System Architecture & Key Features

* **MLOps & Continuous Training (CT):** Fully automated GitHub Actions pipelines that fetch ground-truth telemetry daily, evaluate live model drift (Mean Absolute Error), and retrain the Scikit-Learn Lasso Regression model weekly with zero-downtime `.joblib` deployment.
* **Dual-Layer Caching Strategy:** Redis integration minimizes costly external API calls and ML inference overhead. Current telemetry is cached for 1 hour, while heavy 7-day ML predictions are cached for 24 hours. CI/CD cron jobs act as system heartbeats to ensure caches are always warm for real users.
* **High-Performance Networking:** Custom Vite Proxy configuration bypasses macOS IPv6 DNS resolution and eliminates CORS bottlenecks, bridging the React frontend directly to the Kubernetes Ingress Controller.
* **Resilient Infrastructure:** Backend containerized and deployed on a local Minikube cluster using Helm and Terraform. Configured with Horizontal Pod Autoscaling (HPA) to handle simulated traffic spikes dynamically.
* **Responsive UI:** Built with React & TypeScript, featuring dynamic glassmorphism styling, weather icons, and instant client-side unit conversions (°C ⇄ °F, km/h ⇄ mph).

---

## 🤖 CI/CD & MLOps Pipelines (GitHub Actions)

This project implements a fully automated Continuous Training (CT) and data ingestion architecture. To ensure system stability, every pipeline includes an automated **`pytest` safety gate** that prevents code execution or commits if the unit tests fail.

* **Hourly Telemetry Fetch (`hourly_fetch.yml`):** Runs every hour to fetch the latest weather observations, updates the local CSV dataset, and strategically evicts the 1-hour Redis telemetry cache.
* **Daily Ground Truth Evaluation (`daily_pipeline.yml`):** Runs every night at midnight UTC. It fetches the daily maximum temperature, compares it against the model's prediction from the previous day, logs the Mean Absolute Error (MAE) for drift monitoring, and evicts the 24-hour prediction cache.
* **Weekly Model Retraining (`weekly_retrain.yml`):** Runs every Sunday. It automatically re-runs the feature engineering pipeline on the newly expanded dataset, retrains the Scikit-Learn Lasso model, and commits the updated `.joblib` model back to the repository with zero downtime.

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
* **Orchestration:** Kubernetes (Minikube), Helm Charts, Ingress-Nginx
* **Infrastructure as Code (IaC):** Terraform
* **CI/CD:** GitHub Actions (Cron triggers, automated commits)
* **Testing & Monitoring:** Locust, Pytest, Prometheus, Grafana

---

## 📂 Project Structure

```bash
WeatherForecast/
├── .github/workflows/          # Automated MLOps cron jobs (Hourly, Daily, Weekly)
├── backend/                    # Python FastAPI & ML Pipeline
│   ├── data/                   # Raw CSVs, JSONL logs, and Grafana dashboards
│   ├── models/                 # Serialized ML models (.joblib)
│   ├── src/                    # FastAPI application and ML source code
│   │   ├── main.py             # FastAPI routing and middleware
│   │   ├── pipeline.py         # Telemetry fetching and ground-truth evaluation
│   │   ├── preprocessing.py    # Feature engineering for ML
│   │   ├── schemas.py          # Pydantic response models
│   │   └── train.py            # Model retraining script
│   ├── terraform/              # IaC to provision Kubernetes resources
│   ├── weather-chart/          # Helm chart for Kubernetes deployment
│   ├── Dockerfile              # Backend container build instructions
│   ├── locustfile.py           # Load testing configuration
│   ├── Makefile                # Automation commands for local setup
│   └── uv.lock                 # Strict dependency locking via uv
└── frontend/                   # React + TypeScript Web App
    ├── public/                 # Static assets
    ├── src/
    │   ├── components/         # Modular React components
    │   └── App.tsx             # Root application component
    ├── package.json            # Node dependencies
    └── vite.config.ts          # Vite proxy and bundler configuration
```

---

## 💻 Local Development Setup

This project is designed to be run entirely locally. The backend utilizes a `Makefile` to automate the complex orchestration of Docker, Minikube, and Terraform.

### Prerequisites
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

# Open the network tunnel to expose the local Ingress (requires sudo password)
# NOTE: Leave this terminal window running!
make tunnel
```

### 2. Start the Frontend (React UI)
Open a **new** terminal window, navigate to the frontend directory, and start the Vite development server. The `vite.config.ts` is configured to proxy API requests to the Kubernetes Ingress automatically.

```bash
cd frontend

# Install Node dependencies
npm install

# Start the frontend dev server
npm run dev
```
*The Web UI is now accessible at `http://localhost:5173` (or the port Vite provides).*

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