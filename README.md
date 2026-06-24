# US / Israel–Iran War — NLP Web App

An interactive web app for exploring online discourse about the US/Israel–Iran
war. Two parts:

1. **Insights dashboard** — topic distributions, sentiment charts, source and
   media-type comparisons, conflict-dimension breakdowns, and per-topic word clouds.
2. **Live analyzer** — paste any text and get back a predicted topic (LDA) plus
   VADER and TextBlob sentiment, computed live.

Built with **React (Vite)** + **FastAPI**.

## Architecture

```
backend/     FastAPI API + NLP logic; ships with precomputed data/ and models/
frontend/    React (Vite) dashboard + analyzer
```

The dashboard reads precomputed results, and `/api/analyze` runs live inference —
both share the same NLP logic so results stay consistent.

## Run locally

```bash
git clone https://github.com/Elraph-a/us-israel-iran-war-nlp.git
cd us-israel-iran-war-nlp
```

**Backend** (http://localhost:8000):

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend** (http://localhost:5173) — in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The app runs from the committed `backend/data/` and `backend/models/`, so no
dataset is required. NLTK corpora download automatically on first run.

> To point the frontend at a non-local API, set `VITE_API_URL` before `npm run dev`.

## Deploy

Set up for **Vercel** (frontend) + **Render** (backend). See [DEPLOY.md](DEPLOY.md).
