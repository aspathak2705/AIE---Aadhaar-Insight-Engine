# AIE (Aadhaar Insight Engine)

AIE is a dashboard for exploring Aadhaar-related anomaly signals across India. The project has:

- a FastAPI backend in `backend/`
- a React + Vite frontend in `frontend/`
- a SQLite analytics database in `data/aadhaar.db`

## Local Development

### Backend

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
http://127.0.0.1:8000/api/health
```

### Frontend

Create a frontend env file from the example:

```bash
cp frontend/.env.example frontend/.env
```

On Windows PowerShell:

```powershell
Copy-Item frontend/.env.example frontend/.env
```

Install dependencies and start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Default frontend URL:

```text
http://127.0.0.1:5173
```

## Environment Variables

### Frontend

`frontend/.env`

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Backend

Set allowed frontend origins with a comma-separated list:

```env
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

Optional runtime variables:

```env
PORT=8000
ENV=production
```

## Deployment

### Recommended Setup

- Deploy the backend as a Python web service
- Deploy the frontend as a static site

A practical combination is:

- Backend: Render / Railway / Fly.io
- Frontend: Vercel / Netlify / Cloudflare Pages

### Backend Deployment

The backend entrypoint is:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Make sure these files are included in the deployment:

- `backend/`
- `data/aadhaar.db`
- `requirements.txt`

Set:

- `ENV=production`
- `ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app`

### Frontend Deployment

In the frontend project, set:

```env
VITE_API_BASE_URL=https://your-backend-domain.onrender.com
```

Build command:

```bash
npm run build
```

Output directory:

```text
frontend/dist
```

For Vercel, the repo already includes:

- `frontend/vercel.json` for SPA route rewrites

Recommended Vercel settings:

- Framework Preset: `Vite`
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`

### Render Backend Deployment

The repo includes:

- `render.yaml`

That lets Render create the backend service with the correct start command. After connecting the repo, set:

- `ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app`

## Notes

- The backend is currently read-only against SQLite, which is fine for a lightweight analytics dashboard.
- If traffic grows, consider moving from SQLite to Postgres.
- Some map assets use older administrative boundaries from DataMeet community map sources.
