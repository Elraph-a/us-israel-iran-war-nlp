"""Precompute the NLP analysis once and persist results + fitted models.

Reads the team's cleaned dataset (`cleaned_output2.xlsx`), reruns the exact
LDA / VADER / TextBlob pipeline from `US-Israel-Iran War.ipynb`, and writes:

    backend/data/overview.json
    backend/data/topics.json
    backend/data/sentiment.json
    backend/models/lda.joblib
    backend/models/count_vectorizer.joblib
    backend/models/topic_labels.json

The FastAPI app then just loads these — no heavy recompute at runtime.

Run:  python precompute.py
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

import nlp

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
DATA_XLSX = PROJECT / "cleaned_output2.xlsx"
DATA_DIR = BASE / "data"
MODELS_DIR = BASE / "models"
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 122


def _round(x, n=4):
    try:
        return round(float(x), n)
    except (TypeError, ValueError):
        return None


def main() -> None:
    print(f"Loading dataset: {DATA_XLSX}")
    df = pd.read_excel(DATA_XLSX)
    df["clean_text"] = df["clean_text"].fillna("").astype(str)
    df["lemmatized_text"] = df["lemmatized_text"].fillna("").astype(str)
    print(f"  rows: {len(df):,}  columns: {list(df.columns)}")

    # ---------------------------------------------------------------- TOPICS
    print("Fitting LDA topic model (6 topics)...")
    docs = df["lemmatized_text"].tolist()
    count_vectorizer = CountVectorizer(
        min_df=5, max_df=0.5, max_features=5000,
        ngram_range=(1, 2), stop_words="english",
    )
    count_matrix = count_vectorizer.fit_transform(docs)

    lda_model = LatentDirichletAllocation(
        n_components=6, random_state=RANDOM_STATE, max_iter=100,
    )
    lda_model.fit(count_matrix)

    vocab = count_vectorizer.get_feature_names_out()
    doc_topic = lda_model.transform(count_matrix)
    df["topic_id"] = np.argmax(doc_topic, axis=1)
    df["topic_score"] = np.max(doc_topic, axis=1)

    # Map fitted topic indices to human labels by keyword overlap (robust to
    # scikit-learn's arbitrary topic ordering).
    topic_labels = nlp.label_lda_topics(lda_model, vocab)
    df["topic_label"] = df["topic_id"].map(topic_labels)
    print("  topic label assignment:")
    for i in range(6):
        top = [str(vocab[j]) for j in lda_model.components_[i].argsort()[::-1][:6]]
        print(f"    Topic {i + 1}: {topic_labels[i]}  <-  {', '.join(top)}")

    # Top keywords + weights per topic (for client word clouds)
    topics_keywords = []
    for idx, comp in enumerate(lda_model.components_):
        top = comp.argsort()[::-1][:25]
        weights = comp[top]
        norm = weights / weights.max()
        topics_keywords.append({
            "id": idx,
            "label": topic_labels[idx],
            "keywords": [
                {"word": str(vocab[i]), "weight": _round(w, 4)}
                for i, w in zip(top, norm)
            ],
        })

    # Topic sizes
    sizes = df["topic_id"].value_counts().sort_index()
    total = int(sizes.sum())
    topic_sizes = [
        {
            "id": int(i),
            "label": topic_labels[int(i)],
            "count": int(c),
            "percentage": _round(c / total * 100, 1),
        }
        for i, c in sizes.items()
    ]

    # Topic x Source crosstab (for stacked bar)
    crosstab = pd.crosstab(df["Source"], df["topic_label"])
    topic_by_source = []
    for source, row in crosstab.iterrows():
        entry = {"source": str(source)}
        for label, val in row.items():
            entry[str(label)] = int(val)
        topic_by_source.append(entry)

    topics_json = {
        "topics": topics_keywords,
        "sizes": topic_sizes,
        "by_source": topic_by_source,
        "topic_labels": [topic_labels[i] for i in range(6)],
    }
    (DATA_DIR / "topics.json").write_text(json.dumps(topics_json, indent=2), encoding="utf-8")
    print("  wrote data/topics.json")

    # ------------------------------------------------------------- SENTIMENT
    print("Scoring VADER + TextBlob sentiment...")
    df["vader_compound"] = df["clean_text"].apply(nlp.vader_score)
    df["vader_label"] = df["vader_compound"].apply(nlp.classify_vader)
    df["tb_score"] = df["clean_text"].apply(nlp.textblob_score)
    df["tb_label"] = df["tb_score"].apply(nlp.classify_textblob)
    df["media_type"] = df["Source"].apply(nlp.media_type)

    def dist(series):
        vc = series.value_counts()
        return {
            "Positive": int(vc.get("Positive", 0)),
            "Neutral": int(vc.get("Neutral", 0)),
            "Negative": int(vc.get("Negative", 0)),
        }

    # avg by source
    by_source = []
    for source, sub in df.groupby("Source"):
        by_source.append({
            "source": str(source),
            "vader_avg": _round(sub["vader_compound"].mean()),
            "textblob_avg": _round(sub["tb_score"].mean()),
            "count": int(len(sub)),
        })
    by_source.sort(key=lambda r: r["vader_avg"])

    # news vs social
    media = []
    for mt, sub in df.groupby("media_type"):
        d = dist(sub["vader_label"])
        n = len(sub)
        media.append({
            "media_type": mt,
            "vader_avg": _round(sub["vader_compound"].mean()),
            "count": int(n),
            "pos_pct": _round((sub["vader_label"] == "Positive").mean() * 100, 1),
            "neu_pct": _round((sub["vader_label"] == "Neutral").mean() * 100, 1),
            "neg_pct": _round((sub["vader_label"] == "Negative").mean() * 100, 1),
        })

    # conflict dimensions (VADER avg)
    dimensions = []
    for name, kws in nlp.DIMENSION_KEYWORDS.items():
        mask = df["clean_text"].str.contains("|".join(kws), case=False, na=False)
        sub = df[mask]
        dimensions.append({
            "dimension": name,
            "vader_avg": _round(sub["vader_compound"].mean()),
            "count": int(len(sub)),
        })

    # ---- supervised model accuracy (reported, mirrors notebook) ----
    print("Training supervised classifier for reported accuracy...")
    tfidf = TfidfVectorizer(max_features=5000)
    X = tfidf.fit_transform(df["lemmatized_text"])
    y = df["vader_label"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = LogisticRegression(max_iter=10000)
    clf.fit(X_tr, y_tr)
    acc = accuracy_score(y_te, clf.predict(X_te))

    sentiment_json = {
        "vader_distribution": dist(df["vader_label"]),
        "textblob_distribution": dist(df["tb_label"]),
        "vader_overall_avg": _round(df["vader_compound"].mean()),
        "textblob_overall_avg": _round(df["tb_score"].mean()),
        "by_source": by_source,
        "media_comparison": media,
        "dimensions": dimensions,
        "supervised_accuracy": _round(acc, 4),
    }
    (DATA_DIR / "sentiment.json").write_text(json.dumps(sentiment_json, indent=2), encoding="utf-8")
    print(f"  wrote data/sentiment.json (supervised acc={acc:.4f})")

    # -------------------------------------------------------------- OVERVIEW
    src_counts = df["Source"].value_counts()
    overview_json = {
        "total_documents": int(len(df)),
        "num_sources": int(df["Source"].nunique()),
        "num_topics": 6,
        "sources": [
            {"source": str(s), "count": int(c), "media_type": nlp.media_type(str(s))}
            for s, c in src_counts.items()
        ],
        "scope": "Online discourse on the US / Israel-Iran war, collected across "
                 "news outlets and five social platforms.",
        "methods": [
            "Text preprocessing (cleaning, lemmatization, English filtering)",
            "LDA topic modelling (6 topics)",
            "VADER lexicon sentiment",
            "TextBlob polarity sentiment",
            "Supervised (TF-IDF + Logistic Regression) & unsupervised analysis",
        ],
    }
    (DATA_DIR / "overview.json").write_text(json.dumps(overview_json, indent=2), encoding="utf-8")
    print("  wrote data/overview.json")

    # ---------------------------------------------------------------- MODELS
    joblib.dump(lda_model, MODELS_DIR / "lda.joblib")
    joblib.dump(count_vectorizer, MODELS_DIR / "count_vectorizer.joblib")
    (MODELS_DIR / "topic_labels.json").write_text(
        json.dumps({str(k): v for k, v in topic_labels.items()}, indent=2),
        encoding="utf-8",
    )
    print("  wrote models/lda.joblib, count_vectorizer.joblib, topic_labels.json")
    print("\nDone.")


if __name__ == "__main__":
    main()
