"""FastAPI backend for the US/Israel-Iran War NLP web app.

Serves the precomputed dashboard JSON and a live `/api/analyze` endpoint that
runs LDA topic + VADER + TextBlob inference on user-supplied text.

Run:  uvicorn main:app --reload
(make sure `python precompute.py` has been run first)
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import nlp

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
MODELS_DIR = BASE / "models"

app = FastAPI(
    title="US/Israel-Iran War — NLP API",
    description="Topic modelling & sentiment analysis of online war discourse.",
    version="1.0.0",
)

# Allowed origins: local dev by default, plus any extra origins from the
# FRONTEND_ORIGIN env var (comma-separated). Any *.vercel.app preview/prod
# deployment is also allowed via regex, so the Vercel URL works out of the box.
_default_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
_env_origins = [
    o.strip() for o in os.environ.get("FRONTEND_ORIGIN", "").split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _env_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_json(name: str) -> dict:
    path = DATA_DIR / name
    if not path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"{name} not found. Run `python precompute.py` first.",
        )
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _models():
    lda_path = MODELS_DIR / "lda.joblib"
    cv_path = MODELS_DIR / "count_vectorizer.joblib"
    labels_path = MODELS_DIR / "topic_labels.json"
    if not (lda_path.exists() and cv_path.exists()):
        raise HTTPException(
            status_code=503,
            detail="Models not found. Run `python precompute.py` first.",
        )
    lda = joblib.load(lda_path)
    cv = joblib.load(cv_path)
    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    return lda, cv, labels


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw text to analyze")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/overview")
def overview():
    return _load_json("overview.json")


@app.get("/api/topics")
def topics():
    return _load_json("topics.json")


@app.get("/api/sentiment")
def sentiment():
    return _load_json("sentiment.json")


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text must not be empty.")
    lda, cv, labels = _models()
    return nlp.analyze_text(text, cv, lda, labels)
