# 🌤️ WeatherForecast: Automated MLOps & Observability Architecture

![Weather UI Dashboard](./assets/UI.png)

A high-performance, full-stack weather dashboard and 7-day Machine Learning temperature forecasting platform for Dallas, TX. This project demonstrates an end-to-end production MLOps system featuring automated Continuous Training (CT) pipelines, Redis telemetry caching, multi-worker FastAPI concurrency, and full-stack observability with Prometheus and Grafana.

---

## ✨ System Architecture & Key Features

- **MLOps & Continuous Training (CT):** Automated GitHub Actions pipelines that fetch real-world weather observations daily, evaluate ground-truth model drift (Mean Absolute Error), and retrain the Scikit-Learn Lasso Regression model weekly with automated versioning.
- **Sub-Millisecond In-Memory Caching:** Redis caching strategy that eliminates redundant external API calls and heavy Pandas feature engineering. Live telemetry is cached for 1 hour, and 7-day ML forecasts are cached with a 24-hour TTL (`CACHE_TTL_PREDICT = 86400`).
- **High-Resolution Observability Stack:** Prometheus and Grafana integration via `prometheus-fastapi-instrumentator` with custom sub-millisecond histogram buckets (`1ms` to `1s+`), providing true p50, p90, p95, and p99 latency monitoring in real time.
- **Robust DNS & Networking Architecture:** Optimized Docker internal bridge networking for inter-service container resolution (`backend:8000`, `prometheus:9090`, `redis:6379`), paired with direct IPv4 loopback (`127.0.0.1`) host bindings to eliminate macOS `mDNSResponder` / IPv6 DNS bottlenecks.
- **High-Throughput Concurrency:** Uvicorn configured with 4 asynchronous worker processes (`--workers 4`), handling 300+ RPS under heavy load with zero dropped connections.
- **Responsive React Frontend:** Built with React 19, TypeScript, and Vite, featuring dynamic glassmorphism styling, animated weather visuals, and instant client-side unit toggling (°C ⇄ °F, km/h ⇄ mph, hPa ⇄ inHg).

---

## 🤖 CI/CD & MLOps Pipelines (GitHub Actions)

Every automated pipeline runs with automated **`pytest` safety gates** to guarantee code correctness before committing updates:

- **Daily Pipeline & Ground Truth Evaluation (`daily_pipeline.yml`):** Runs every night at 00:00 CDT (05:00 UTC). It fetches the previous day's verified temperature observations from Open-Meteo, calculates the Mean Absolute Error (MAE) against previous forecasts for drift tracking, and automatically commits updated datasets to the repository. Runs against a transient GitHub Actions Redis service container.
- **Weekly Model Retraining (`weekly_retrain.yml`):** Runs every Sunday at 00:30 CDT (05:30 UTC). Automatically runs feature engineering over the expanded historical dataset, retrains the Scikit-Learn multi-output Lasso regression pipeline, and commits the serialized `.joblib` model artifact back to the repository with zero downtime.

---

## 🏗️ Tech Stack

### Frontend
- **Framework:** React 19, TypeScript, Vite
- **Styling:** Vanilla CSS (Glassmorphism design system)
- **State & Networking:** React Hooks, Vite HTTP Proxy

### Backend & Machine Learning
- **API Framework:** Python 3.11/3.13, FastAPI, Uvicorn (Multi-Worker)
- **Data Science & ML:** Pandas, NumPy, Scikit-Learn (Lasso Multi-Output Regressor)
- **Caching Layer:** Redis 7 (Alpine) with `fakeredis` local fallback
- **Package Management:** `uv` (Fast Python package resolver)

### DevOps & Observability
- **Container Orchestration:** Docker Compose (Multi-Service Stack)
- **Metrics Collection:** Prometheus (`prom/prometheus:latest`)
- **Telemetry Dashboards:** Grafana (`grafana/grafana:latest`)
- **Load Testing:** Locust
- **CI/CD:** GitHub Actions (Service containers, autostash git syncing)

---

## 📂 Project Structure

```bash
WeatherForecast/
├── .github/workflows/          # Automated MLOps cron jobs
│   ├── daily_pipeline.yml      # Daily data ingestion & MAE evaluation
│   └── weekly_retrain.yml      # Weekly automated model retraining
├── assets/                     # UI screenshots and performance benchmark graphs
├── backend/                    # Python FastAPI & ML Service
│   ├── data/                   # Historical observations & evaluation logs
│   │   ├── meteostat_export.csv # 3-year sliding historical dataset
│   │   ├── predictions_log.jsonl # Historical model predictions log
│   │   └── evaluations_log.jsonl # Ground-truth daily error tracking
│   ├── models/                 # Serialized ML model artifacts (.joblib)
│   ├── src/                    # Backend application source code
│   │   ├── config.py           # Centralized configuration & Redis TTLs
│   │   ├── main.py             # FastAPI routes, Prometheus instrumentation & health checks
│   │   ├── pipeline.py         # Data ingestion, Open-Meteo sync & MAE evaluation
│   │   ├── preprocessing.py    # Feature engineering (rolling means, lags)
│   │   ├── schemas.py          # Pydantic response models
│   │   ├── train.py            # Scikit-Learn Lasso training script
│   │   └── warm_cache.py       # Cache pre-warming utility script
│   ├── tests/                  # Automated pytest test suite
│   │   ├── test_api.py         # Endpoint and Redis integration tests
│   │   └── test_preprocessing.py # Feature engineering unit tests
│   ├── Dockerfile              # Production multi-worker backend container
│   ├── docker-compose.yml      # Multi-container orchestration (API, Redis, Prom, Grafana)
│   ├── grafana_dashboard.json  # Pre-configured Grafana monitoring dashboard
│   ├── locustfile.py           # Locust load testing scenario
│   ├── Makefile                # Unified developer CLI for stack management
│   ├── prometheus.yml          # Prometheus scrape configuration
│   ├── pyproject.toml          # Python package specification
│   └── uv.lock                 # Strict dependency locking via uv
└── frontend/                   # React + TypeScript Web Application
    ├── src/
    │   ├── components/         # Modular UI components (Current, Forecast, Details)
    │   ├── types/              # TypeScript weather domain interfaces
    │   ├── utils/              # Unit conversion & weather visual helpers
    │   └── App.tsx             # Root React application
    ├── package.json            # Node.js dependencies
    └── vite.config.ts          # Vite configuration & backend proxy
```

---

## 💻 Local Development Setup

The backend utilizes a clean `Makefile` to manage the lifecycle of all Docker containers, caching, and testing tools.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or OrbStack
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Node.js](https://nodejs.org/) (v18+) & `npm`

---

### 1. Start the Backend Stack (Docker Compose)

Navigate to the `backend/` directory and spin up the complete containerized environment (FastAPI, Redis, Prometheus, and Grafana):

```bash
cd backend

# Build and start all 4 services in the background
make up

# (Optional) Pre-warm the Redis cache for instant first-hit responses
make warm
```

Verify that all services are healthy:
```bash
make ps
```

| Service | Container Name | Host URL | Description |
| :--- | :--- | :--- | :--- |
| **FastAPI Backend** | `weather_api_backend` | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive Swagger API & metrics |
| **Grafana Dashboard** | `weather_grafana` | [http://127.0.0.1:3000](http://127.0.0.1:3000) | Live SRE & MLOps performance dashboards |
| **Prometheus Server** | `weather_prometheus` | [http://127.0.0.1:9090](http://127.0.0.1:9090) | PromQL query engine & target scrapers |
| **Redis Cache** | `weather_redis` | `127.0.0.1:6379` | In-memory telemetry and forecast caching |

---

### 2. Configure Grafana Dashboard

1. Open **[http://127.0.0.1:3000](http://127.0.0.1:3000)** in your browser (*Default login: `admin` / `admin`*).
2. Go to **Connections $\to$ Data Sources $\to$ Add data source $\to$ Prometheus**.
3. In **Prometheus server URL**, enter the internal Docker DNS name:
   ```text
   http://prometheus:9090
   ```
4. Click **Save & test** (Confirm green checkmark).
5. Go to **Dashboards $\to$ New $\to$ Import**, upload [`backend/grafana_dashboard.json`](./backend/grafana_dashboard.json), select the Prometheus datasource, and click **Import**.

---

### 3. Start the Frontend (React UI)

In a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Launch Vite development server
npm run dev
```

Open **[http://localhost:5173](http://localhost:5173)** to view the live weather application.

---

### 4. Run Load Testing & Stress Verification

Simulate concurrent production traffic against the API to observe live throughput and latency curves in Grafana:

```bash
cd backend
make test
```

1. Open **[http://127.0.0.1:8089](http://127.0.0.1:8089)** in your browser.
2. Set **Number of users** to `150` and **Spawn rate** to `5`.
3. Set **Host** to `http://weather.local` (or `http://127.0.0.1:8000`).
4. Click **Start Swarming** and watch live percentiles in Grafana.

---

## ⚡ Performance & Benchmark Results

### High-Concurrency Stress Test (150 Users, ~450 RPS)

Under sustained high-frequency load testing across **33,500+ requests** with 150 simulated concurrent users:

| Metric | Locust (Client Round-Trip) | Grafana / Prometheus (Server Processing) |
| :--- | :--- | :--- |
| **Current / Peak Throughput** | **450.7 RPS** | **4.86K req/s** (Peak Rate) |
| **Success Rate / Error Ratio**| **100%** (0% failures) | **100% HTTP 2xx** (0 HTTP 4xx/5xx) |
| **Average Response Time** | **29.75 ms** | ~8.20 ms |
| **Median Latency (p50)** | **44 ms** | ~8.00 ms |
| **p95 Latency** | **51 ms** | **9.53 ms** |
| **p99 Tail Latency** | **56 ms** | **9.93 ms** |
| **Max Recorded Latency** | **98 ms** | ~95.4 ms (Burst spike on `/predict`) |

---

### Benchmark Artifacts

![Locust Load Test Performance](./assets/Locust_150_5_rampup.jpeg)

![Grafana Metrics & SLO Dashboard](./assets/Grafana.jpeg)

---

### Performance & Latency Analysis

* **Sub-10ms Server-Side Latency (p95 & p99):**  
  As captured in Prometheus/Grafana, internal processing overhead remains under **9.53 ms (p95)** and **9.93 ms (p99)** across all endpoints. The internal pipeline processes requests comfortably within strict real-time Service Level Objectives (SLOs).

* **Predictable Tail Latency:**  
  Client-side observations via Locust show a remarkably tight delta of just **12 ms** between median latency (**44 ms**) and the 99th percentile (**56 ms**). This near-flat latency profile demonstrates that the service avoids thread pool exhaustion, unmanaged queue build-up, and garbage-collection stalls during sustained concurrency.

* **100% Availability Under Load:**  
  Across 33,512 dispatched requests encompassing computationally heavier endpoints (`POST /predict?units=imperial`, `POST /predict?units=metric`) and high-volume reads (`GET /today`, `GET /health`), the system maintained a **0.0% failure rate** with zero 4xx/5xx status codes returned.

* **Client Round-Trip Overhead:**  
  The ~15–35 ms delta between Locust client round-trips (median 44 ms) and server-side Prometheus metrics (median ~8 ms) accounts for local TCP handshake overhead, connection pooling, and serialization over HTTP.

## 🧹 Teardown & Maintenance

To stop the running stack and clean up temporary assets:

```bash
cd backend

# Stop and remove all containers and Docker networks
make down

# Clean temporary Python bytecode and test caches
make clean
```
