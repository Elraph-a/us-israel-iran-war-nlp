# Deploying the app (Vercel + Render)

Two services:

- **Backend (FastAPI)** → [Render](https://render.com) free web service
- **Frontend (React/Vite)** → [Vercel](https://vercel.com)

The precomputed `backend/data/` and `backend/models/` are committed to the repo,
so the backend runs without needing the original dataset.

---

## 1. Deploy the backend on Render

1. Push this repo to GitHub (already done if you're reading this from GitHub).
2. On Render: **New + → Blueprint**, select this repository. Render reads
   [`render.yaml`](render.yaml) and creates a web service named
   `war-discourse-api`.
   - _Or_ do it manually: **New + → Web Service** with
     - **Root Directory:** `backend`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Environment variable:** `PYTHON_VERSION = 3.12.10`
3. Deploy. When it's live you'll get a URL like
   `https://war-discourse-api.onrender.com`.
4. Test it: open `<that-url>/api/health` → should return `{"status":"ok"}`.

> **Free tier note:** the service sleeps after ~15 min idle; the first request
> after sleeping takes ~30–50s to wake. That's normal.

---

## 2. Deploy the frontend on Vercel

1. On Vercel: **Add New → Project**, import this repository.
2. Configure the project:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite (auto-detected)
   - Build command / output dir are auto-detected (`npm run build` → `dist`).
3. Add an **Environment Variable**:
   - `VITE_API_URL` = your Render URL, e.g. `https://war-discourse-api.onrender.com`
4. Deploy. You'll get a URL like `https://your-frontend.vercel.app`.

`vercel.json` already handles SPA routing so page refreshes work on every route.

---

## 3. Link the two (CORS)

The backend already allows any `*.vercel.app` origin, so it should work
immediately. To lock it to your exact domain, set this env var on Render and
redeploy:

- `FRONTEND_ORIGIN = https://your-frontend.vercel.app`

---

## Updating after changes

Push to GitHub — Vercel and Render redeploy automatically.

> Keep any API keys in a local `.env` (gitignored); never commit secrets.
