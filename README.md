# 🌤️ WeatherForecast

**Real‑time weather dashboard & 7‑day ML‑powered forecast for Dallas, TX**

> Created by **Gia Nghi Dang** — Computer‑Science student @ University of Texas at Dallas (UTD)

---

## 🚀 Live Demo

| Front‑end | Back‑end docs |
|-----------|---------------|
| <https://weatherforecastfrontend.s3-website.us-east-2.amazonaws.com> | <http://3.141.116.122:8000/docs> |

---

## ✨ Features

- **Live conditions** – current temperature, wind speed & direction, pressure, precipitation  
- **Unit toggle** – instant °C ⇄ °F (and km/h ⇄ mph, hPa ⇄ inHg, mm ⇄ inches)  
- **Theme switcher** – light ↔︎ dark mode with one click  
- **7‑day forecast** – daily high‑temperature outlook 
- **Responsive layout** – optimised for desktop, tablet, and mobile  
- **Dynamic icons & subtle animations** – visuals update automatically with the weather

---

## ⚙️ Tech Stack

| Layer | Tools |
|-------|-------|
| **Front‑end** | React • TypeScript • Vite • CSS |
| **Back‑end** | FastAPI • Uvicorn  |
| **ML / Data** | pandas • scikit‑learn • numpy |
| **Infra** | AWS EC2 (Ubuntu) • AWS S3 (static web hosting) |
| **DevOps** | GitHub Actions • rsync • screen |
| **Scheduling** | `cron` (`hourly_update.py`, `daily_update.py`) |

---

## 🧠 Model Training Details

| Item | Value |
|------|-------|
| Target | Daily maximum temperature (°C) |
| Algorithm | **Lasso Regression** |
| Features | Rolling mean (7/14 days), percentage difference, expanding monthly/daily averages, etc. |
| Data Source | Meteostat® DFW station, 2022‑07‑26 → present |
| Validation | Time‑series split • MAE ≈ 3.97 °C |

---

## 🖥️ Local Development

```bash
# Clone & set up backend
git clone https://github.com/gia-nghi159/WeatherForecast.git
cd WeatherForecast
python -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt

# Run API
uvicorn backend.app.api:app --reload

# In a second terminal: front‑end
cd frontend
npm i
npm run dev

