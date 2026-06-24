import { useState } from "react";
import { analyzeText } from "../api.js";
import { SentimentBadge } from "../components/common.jsx";

const EXAMPLES = [
  "Iran launched a barrage of ballistic missiles at Israel overnight, killing several civilians.",
  "Diplomats from both sides met in Geneva today, raising cautious hopes for a ceasefire.",
  "Oil prices surged as fears grew over a possible closure of the Strait of Hormuz.",
  "Honestly the media coverage of this war is full of bias and propaganda.",
];

export default function Analyzer() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function run() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await analyzeText(text);
      setResult(r);
    } catch (e) {
      setError(
        e?.response?.data?.detail ||
          e?.message ||
          "Request failed. Is the backend running on :8000?"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1>Live Analyzer</h1>
      <p className="subtitle">
        Paste any text about the conflict. The trained LDA model assigns a
        topic, and VADER + TextBlob score the sentiment — in real time.
      </p>

      <div className="card">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="e.g. Iran fired missiles at Israeli air bases overnight…"
        />
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 14 }}>
          <button className="btn" onClick={run} disabled={loading || !text.trim()}>
            {loading ? "Analyzing…" : "Analyze"}
          </button>
          <span className="muted" style={{ fontSize: 13 }}>
            {text.length} characters
          </span>
        </div>

        <div className="chips">
          <span className="muted" style={{ fontSize: 13, marginRight: 4 }}>
            Try:
          </span>
          {EXAMPLES.map((ex, i) => (
            <span className="chip" key={i} onClick={() => setText(ex)}>
              {ex.slice(0, 42)}…
            </span>
          ))}
        </div>
      </div>

      {error && (
        <div className="error" style={{ padding: "24px 0" }}>
          ⚠ {error}
        </div>
      )}

      {result && (
        <>
          <div className="result-grid">
            <div className="result-box">
              <div className="k">Predicted topic</div>
              <div className="v">{result.topic.label || "—"}</div>
              <div className="muted" style={{ fontSize: 13, marginTop: 6 }}>
                {result.topic.id !== null
                  ? `Topic ${result.topic.id + 1} · confidence ${(
                      result.topic.score * 100
                    ).toFixed(0)}%`
                  : "Not enough recognizable content"}
              </div>
            </div>

            <div className="result-box">
              <div className="k">VADER sentiment</div>
              <div className="v">
                <SentimentBadge label={result.vader.label} />
              </div>
              <div className="muted" style={{ fontSize: 13, marginTop: 6 }}>
                compound = {result.vader.compound}
              </div>
            </div>

            <div className="result-box">
              <div className="k">TextBlob sentiment</div>
              <div className="v">
                <SentimentBadge label={result.textblob.label} />
              </div>
              <div className="muted" style={{ fontSize: 13, marginTop: 6 }}>
                polarity = {result.textblob.polarity}
              </div>
            </div>
          </div>

          <div className="card" style={{ marginTop: 18 }}>
            <div className="k muted" style={{ fontSize: 12, textTransform: "uppercase" }}>
              Cleaned text (what the model saw)
            </div>
            <p style={{ marginBottom: 0 }}>
              {result.clean_text || <span className="muted">(empty after cleaning)</span>}
            </p>
          </div>
        </>
      )}
    </>
  );
}
