export default function About() {
  return (
    <>
      <h1>About this project</h1>
      <p className="subtitle">
        An NLP project analyzing online discourse on the US / Israel–Iran war.
      </p>

      <div className="card">
        <h2 style={{ marginTop: 0 }}>Data collection</h2>
        <p className="muted">
          Over nine thousand documents were gathered across news outlets and
          several social platforms:
        </p>
        <div>
          {["News Outlets", "Facebook", "TikTok", "Twitter / X", "YouTube", "Reddit", "Instagram"].map(
            (s) => (
              <span className="tag" key={s}>
                {s}
              </span>
            )
          )}
        </div>
      </div>

      <div className="card" style={{ marginTop: 18 }}>
        <h2 style={{ marginTop: 0 }}>Analysis pipeline</h2>
        <ul className="clean">
          <li>
            <strong>Preprocessing</strong> — lowercasing, emoji/URL/HTML removal,
            punctuation &amp; stopword stripping, POS-aware lemmatization, and
            English-language filtering.
          </li>
          <li>
            <strong>Topic modelling</strong> — Latent Dirichlet Allocation (LDA)
            over a CountVectorizer document-term matrix, yielding six topics.
          </li>
          <li>
            <strong>Sentiment</strong> — VADER (lexicon, compound score) and
            TextBlob (polarity), each classified into Positive / Neutral /
            Negative.
          </li>
          <li>
            <strong>Modelling</strong> — supervised TF-IDF + Logistic Regression
            classifier alongside unsupervised K-Means clustering.
          </li>
        </ul>
      </div>

      <div className="card" style={{ marginTop: 18 }}>
        <h2 style={{ marginTop: 0 }}>How this app works</h2>
        <p className="muted">
          The dashboard reads results precomputed once from the team's cleaned
          dataset. The Analyzer calls a FastAPI backend that loads the trained
          LDA model and runs VADER + TextBlob live on your input — using the
          exact preprocessing from the original notebook, so live results stay
          consistent with the dashboard.
        </p>
      </div>

      <p className="muted center" style={{ marginTop: 28 }}>
        Built from <code>US-Israel-Iran War.ipynb</code> · React + FastAPI
      </p>
    </>
  );
}
