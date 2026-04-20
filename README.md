<div align="center">
  <img src="https://img.icons8.com/color/96/000000/combo-chart--v1.png" alt="AIE Logo" width="80" />
  <h1 align="center">AIE (Aadhaar Insight Engine)</h1>
  <p align="center">
    <strong>A geospatial anomaly intelligence dashboard for Aadhaar activity analysis across India</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Frontend-React%20%7C%20Vite-61DAFB" alt="Frontend" />
    <img src="https://img.shields.io/badge/Backend-FastAPI-009688" alt="Backend" />
    <img src="https://img.shields.io/badge/Database-SQLite-003B57" alt="Database" />
    <img src="https://img.shields.io/badge/Charts-Recharts%20%7C%20Plotly-6C63FF" alt="Charts" />
  </p>
</div>

---

## Overview

**AIE (Aadhaar Insight Engine)** is an analytical dashboard designed to surface unusual Aadhaar activity patterns through geographic, temporal, and statistical views.

The system combines:

- a **FastAPI** backend for lightweight analytics APIs
- a **React + Vite** frontend for interactive dashboards
- a local **SQLite** database containing precomputed regional and monthly features
- map-based drilldowns for state and district exploration

The current product experience is built around rapid anomaly inspection, helping users move from national overview to state and district-level investigation.

<br>

## Key Features

- **System Overview Dashboard:** Summarizes total monitored regions, average anomaly score, critical anomalies, and highest observed activity ratios.
- **Geospatial Drilldown Intelligence:** Starts with an India-wide state map and lets users click into district-level maps for a selected state.
- **Temporal Analysis:** Tracks activity trends over time with national, state, and district filters.
- **Distribution Analysis:** Converts statistical spread into more user-friendly summaries of low, typical, and high activity levels.
- **Deep Investigation Workflow:** Helps users inspect suspicious districts and pincodes with ranked anomaly scores.
- **Portable Data Stack:** Runs entirely on a SQLite-backed analytics dataset without requiring a separate managed database for small deployments.

<br>

## Architecture & Tech Stack

This project is split into two main layers: a frontend single-page application and a backend analytics API.

### Frontend

- **Framework:** React 19 + Vite
- **Routing:** React Router
- **HTTP Client:** Axios
- **Visualization:** Recharts + Plotly
- **Styling:** Custom CSS design system
- **Deployment Strategy:** Vercel / Netlify / any static host

### Backend

- **Framework:** FastAPI
- **Server:** Uvicorn
- **Data Processing:** Pandas
- **Storage:** SQLite
- **Deployment Strategy:** Render / Railway / Fly.io / VPS

### Data Layer

- **Primary Database:** `data/aadhaar.db`
- **Core Tables:**
  - `regional_features`
  - `monthly_features`
- **Derived Metrics:**
  - `anomaly_score`
  - `activity_ratio`
  - `bio_share`
  - `demo_share`

<br>

## Product Modules

The dashboard is organized into the following analytical views:

- **Overview:** High-level KPIs and top-risk regions
- **Geo Intelligence:** India state map with district drilldown
- **Temporal Analysis:** Trend view over monthly activity ratios
- **Distribution Analysis:** Histogram and plain-language activity range summary
- **Investigation:** District and pincode-level risk inspection

<br>

## Project Structure

```text
AIE (Aadhaar Insight Engine)/
├── backend/                 # FastAPI backend
├── frontend/                # React + Vite frontend
├── data/                    # SQLite DB and processed datasets
├── database/                # Database setup helpers
├── src/                     # Older feature engineering / anomaly pipeline
├── requirements.txt
├── render.yaml
└── README.md
```

<br>

## Getting Started (Local Development)

### Prerequisites

- Node.js `18+`
- Python `3.10+`
- `pip` available in your Python environment

### 1. Backend Setup

Install dependencies from the project root:

```bash
pip install -r requirements.txt
```

Run the FastAPI backend:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

If `uvicorn` is not recognized:

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Available backend URLs:

- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

### 2. Frontend Setup

Create a frontend env file:

```bash
cp frontend/.env.example frontend/.env
```

On Windows PowerShell:

```powershell
Copy-Item frontend/.env.example frontend/.env
```

Then install and run the frontend:

```bash
cd frontend
npm install
npm run dev
```

Default frontend URL:

```text
http://127.0.0.1:5173
```

<br>

## Environment Configuration

### Frontend

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Backend

Optional backend environment variables:

```env
PORT=8000
ENV=production
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

`ALLOWED_ORIGINS` accepts a comma-separated list when multiple frontend domains need access.

<br>

## API Endpoints Reference

The backend exposes a compact analytics API:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Backend health and database availability check |
| `GET` | `/api/overview` | Dashboard KPIs and top anomaly regions |
| `GET` | `/api/states` | Distinct list of available states |
| `GET` | `/api/geo` | State-level or district-level map data |
| `GET` | `/api/temporal` | Monthly activity trend data |
| `GET` | `/api/districts` | District list for a selected state |
| `GET` | `/api/distribution` | Histogram, quantiles, and district distribution breakdown |
| `GET` | `/api/investigation` | District and pincode anomaly exploration |

Interactive Swagger docs are automatically available at:

```text
http://127.0.0.1:8000/docs
```

<br>

## Data & Methodology

The dashboard runs on preprocessed feature tables rather than raw transactional data.

At a high level:

1. enrolment, demographic, and biometric datasets are cleaned and merged
2. region-level and monthly aggregates are created
3. semantic ratios such as `activity_ratio`, `bio_share`, and `demo_share` are computed
4. anomaly scoring is derived from normalized activity deviations and outlier flags

The anomaly workflow in the older pipeline under `src/D0_Data_Visualization/` uses:

- z-score based deviation measurement
- IQR-based outlier detection
- weighted combination scoring for `anomaly_score`

<br>

## Deployment

### Recommended Setup

- **Frontend:** Vercel
- **Backend:** Render

This is the easiest production path for the current repo layout.

### Frontend Deployment

Recommended Vercel settings:

- **Framework Preset:** `Vite`
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

Frontend environment variable:

```env
VITE_API_BASE_URL=https://your-backend-domain.onrender.com
```

The repo already includes:

- `frontend/vercel.json` for SPA route rewrites

### Backend Deployment

Recommended Render settings:

- **Language:** `Python 3`
- **Root Directory:** leave blank
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

Backend environment variables:

```env
ENV=production
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

The repo also includes:

- `render.yaml`

Make sure the deployment includes:

- `backend/`
- `data/aadhaar.db`
- `requirements.txt`

<br>

## Current Limitations

- The app currently relies on a local SQLite database, which is suitable for lightweight read-heavy workloads but not ideal for high-scale production.
- Some administrative map assets are based on older boundary datasets and may not reflect the newest state or district boundaries perfectly.
- The frontend bundle is relatively large because Plotly is included for map rendering.

<br>

## Future Improvements

- migrate the analytics store from SQLite to Postgres for larger deployments
- add authentication and role-based access
- support richer investigation workflows and case tracking
- modernize geographic assets with newer India boundary datasets
- add automated tests for API responses and frontend drilldown behavior

---

<div align="center">
  <p>Built for anomaly discovery, regional intelligence, and interactive investigation.</p>
</div>
