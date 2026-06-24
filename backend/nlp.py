"""Shared NLP logic for the US/Israel-Iran War discourse app.

Mirrors the exact preprocessing, lemmatization and sentiment logic from
`US-Israel-Iran War.ipynb` so that live inference in the API matches the precomputed
dashboard numbers. Imported by both `precompute.py` and `main.py`.
"""
from __future__ import annotations

import html as html_mod
import re
import string

import nltk
from nltk import pos_tag
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ----------------------------------------------------------------------------
# NLTK data — download once if missing (quiet, idempotent)
# ----------------------------------------------------------------------------
for _pkg in (
    "stopwords",
    "wordnet",
    "averaged_perceptron_tagger_eng",
    "punkt_tab",
    "vader_lexicon",
):
    try:
        nltk.download(_pkg, quiet=True)
    except Exception:  # pragma: no cover - network/offline tolerance
        pass

# ----------------------------------------------------------------------------
# Stopwords (standard + custom) — copied verbatim from the notebook
# ----------------------------------------------------------------------------
STOPWORDS = set(stopwords.words("english"))

CUSTOM_STOPWORDS = {
    # Social media noise
    "rt", "amp", "via", "like", "lol", "lmao", "lmfao", "omg", "smh",
    "gonna", "gotta", "wanna", "dont", "doesnt", "didnt", "cant", "wont",
    "isnt", "wasnt", "wouldnt", "shouldnt", "couldnt", "aint", "im",
    "ive", "youre", "theyre", "theyve", "weve", "hes", "shes", "thats",
    "whats", "lets", "youve", "youll", "theyll", "hadnt", "hasnt",
    # Reporting / filler verbs
    "said", "reported", "according", "says", "told", "added", "noted",
    # Platform artifacts
    "sticker", "reply", "retweet", "share", "comment", "subscribe",
    "video", "watch", "click", "link", "bio", "follow", "page",
    # Generic filler words common in social media
    "also", "even", "still", "much", "many", "really", "just",
    "thing", "things", "something", "everything", "nothing",
    "anyone", "everyone", "someone", "people", "guy", "guys",
    "got", "get", "gets", "getting", "go", "going", "gone", "went",
    "come", "came", "coming", "back", "well", "way",
    "know", "think", "make", "made", "take", "took",
    "see", "look", "put", "use", "used",
    "one", "two", "would", "could", "may", "might",
    "need", "want", "right", "good", "new", "first", "last", "long",
    "great", "little", "big", "old", "year", "years", "time", "day", "days",
    # News boilerplate
    "bbc", "cnn", "reuters", "associated", "press", "read", "source",
    "updated", "published", "copyright", "reserved", "rights",
    "news", "article", "report",
}

ALL_STOPWORDS = STOPWORDS.union(CUSTOM_STOPWORDS)

_lemmatizer = WordNetLemmatizer()


def preprocess_text(text) -> str:
    """Clean a raw string exactly as the notebook's `preprocess_text` did."""
    if text is None:
        return ""
    text = str(text)
    text = text.lower()
    text = re.sub(r"\[sticker\]", "", text)
    try:
        import emoji
        text = emoji.replace_emoji(text, replace="")
    except Exception:
        pass
    text = re.sub(r"http\S+|www\S+|t\.co/\S+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = html_mod.unescape(text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # strip non-ASCII
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"\b[^ia\s]\b", "", text)  # single-char fragments except i/a
    text = re.sub(r"\s+", " ", text).strip()
    words = [w for w in text.split() if w not in ALL_STOPWORDS]
    return " ".join(words)


def _wordnet_pos(treebank_tag: str):
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    if treebank_tag.startswith("V"):
        return wordnet.VERB
    if treebank_tag.startswith("N"):
        return wordnet.NOUN
    if treebank_tag.startswith("R"):
        return wordnet.ADV
    return wordnet.NOUN


def lemmatize_text(text: str) -> str:
    """POS-tag then lemmatize, matching the notebook's `lemmatize_text`."""
    if not isinstance(text, str) or len(text.strip()) == 0:
        return ""
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    lemmas = [_lemmatizer.lemmatize(w, _wordnet_pos(t)) for w, t in tagged]
    return " ".join(lemmas)


# ----------------------------------------------------------------------------
# Sentiment
# ----------------------------------------------------------------------------
def classify_vader(score: float) -> str:
    if score >= 0.05:
        return "Positive"
    if score <= -0.05:
        return "Negative"
    return "Neutral"


def classify_textblob(score: float) -> str:
    # Notebook used the same +/-0 thresholds via classify_sentiment
    if score > 0:
        return "Positive"
    if score < 0:
        return "Negative"
    return "Neutral"


_sid = None


def _vader():
    global _sid
    if _sid is None:
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        _sid = SentimentIntensityAnalyzer()
    return _sid


def vader_score(text: str) -> float:
    return _vader().polarity_scores(str(text))["compound"]


def textblob_score(text: str) -> float:
    from textblob import TextBlob
    return TextBlob(str(text)).sentiment.polarity


# ----------------------------------------------------------------------------
# Live analysis (topic + both sentiments) — used by the /analyze endpoint
# ----------------------------------------------------------------------------
def analyze_text(raw_text: str, count_vectorizer, lda_model, topic_labels: dict) -> dict:
    """Run the full inference path on a single raw string."""
    clean = preprocess_text(raw_text)
    lemmas = lemmatize_text(clean)

    # Topic via LDA (operates on lemmatized text, as in the notebook)
    topic_id = None
    topic_label = None
    topic_score = 0.0
    if lemmas.strip():
        dist = lda_model.transform(count_vectorizer.transform([lemmas]))[0]
        topic_id = int(dist.argmax())
        topic_score = float(dist.max())
        topic_label = topic_labels.get(str(topic_id), topic_labels.get(topic_id))

    v = vader_score(clean)
    t = textblob_score(clean)

    return {
        "clean_text": clean,
        "topic": {
            "id": topic_id,
            "label": topic_label,
            "score": round(topic_score, 4),
        },
        "vader": {"compound": round(v, 4), "label": classify_vader(v)},
        "textblob": {"polarity": round(t, 4), "label": classify_textblob(t)},
    }


# Human-assigned topic labels from the notebook, each defined by a set of
# signature keywords. LDA topic *indices* are arbitrary and depend on the
# scikit-learn version, so we map fitted topics to these labels by matching
# their top keywords against these signatures (see `label_lda_topics`).
TOPIC_SIGNATURES = {
    "State power, governance & political leadership":
        ["state", "president", "power", "regime", "government", "american", "leadership", "trump"],
    "Regional conflict & proxy warfare (Iran-Israel-Hezbollah)":
        ["lebanon", "hezbollah", "israeli", "kill", "attack", "country", "hamas", "gaza"],
    "Online discourse & nuclear conflict narratives":
        ["post", "help", "nuclear", "mar", "start", "say", "comment", "thread"],
    "Military operations & weapons systems":
        ["missile", "strike", "drone", "target", "force", "weapon", "military", "iranian"],
    "Global energy markets & the Strait of Hormuz":
        ["oil", "price", "energy", "strait", "hormuz", "market", "global", "gas", "trade"],
    "Diplomatic negotiations":
        ["talk", "official", "diplomacy", "negotiation", "end", "deal", "agreement", "ceasefire"],
}


def label_lda_topics(lda_model, vocab, top_n=15):
    """Assign each fitted LDA topic to a human label by optimal keyword overlap.

    Returns {topic_id: label}. Uses a 1-to-1 assignment so each label is used
    once, regardless of how scikit-learn ordered the topics.
    """
    import numpy as np

    labels = list(TOPIC_SIGNATURES.keys())
    n_topics = lda_model.components_.shape[0]

    # top keywords per topic
    topic_words = []
    for comp in lda_model.components_:
        idx = comp.argsort()[::-1][:top_n]
        words = set()
        for i in idx:
            for tok in str(vocab[i]).split():  # split bigrams into unigrams
                words.add(tok)
        topic_words.append(words)

    # overlap score matrix (topics x labels)
    score = np.zeros((n_topics, len(labels)))
    for t, words in enumerate(topic_words):
        for j, lab in enumerate(labels):
            sig = set(TOPIC_SIGNATURES[lab])
            score[t, j] = len(words & sig)

    # optimal 1-to-1 assignment (maximize overlap)
    try:
        from scipy.optimize import linear_sum_assignment
        rows, cols = linear_sum_assignment(-score)
        mapping = {int(r): labels[int(c)] for r, c in zip(rows, cols)}
    except Exception:
        # greedy fallback
        mapping, used = {}, set()
        order = np.dstack(np.unravel_index(np.argsort(-score, axis=None), score.shape))[0]
        for t, j in order:
            if t in mapping or j in used:
                continue
            mapping[int(t)] = labels[int(j)]
            used.add(j)
    return {i: mapping.get(i, f"Topic {i + 1}") for i in range(n_topics)}

# Conflict-dimension keyword sets from the notebook
DIMENSION_KEYWORDS = {
    "Military": ["drone", "missile", "attack", "fighter", "military", "defense", "force", "weapon"],
    "Geopolitical": ["middle east", "africa", "asia", "iran", "israel", "allies", "international", "diplomacy"],
    "Economic": ["oil", "energy", "gas", "strait", "hormuz", "market", "price", "economy", "trade"],
    "Media": ["bbc", "reuters", "media", "misinformation", "bias", "propaganda", "news", "trust", "youtube", "facebook"],
    "Support": ["support", "protest", "peace", "against", "ally", "us", "sanction", "condemn"],
}

SOCIAL_SOURCES = ["Twitter", "Reddit", "YouTube", "Facebook", "TikTok", "Instagram"]


def media_type(source: str) -> str:
    return "Social Media" if source in SOCIAL_SOURCES else "Traditional News"
