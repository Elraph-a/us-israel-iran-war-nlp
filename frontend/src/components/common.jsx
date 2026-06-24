import { useEffect, useState } from "react";

export function useFetch(fn) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    let alive = true;
    fn()
      .then((d) => alive && setData(d))
      .catch((e) =>
        alive &&
        setError(
          e?.response?.data?.detail ||
            e?.message ||
            "Failed to load. Is the backend running on :8000?"
        )
      );
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return { data, error };
}

export function Loading() {
  return <div className="loading">Loading…</div>;
}

export function ErrorBox({ message }) {
  return (
    <div className="error">
      ⚠ {message}
      <div className="muted" style={{ marginTop: 8, fontSize: 13 }}>
        Start the API with: <code>uvicorn main:app --reload</code>
      </div>
    </div>
  );
}

export function StatCard({ value, label }) {
  return (
    <div className="stat">
      <div className="value">{value}</div>
      <div className="label">{label}</div>
    </div>
  );
}

export function ChartCard({ title, hint, children }) {
  return (
    <div className="chart-card">
      <h3>{title}</h3>
      {hint && <p className="hint">{hint}</p>}
      {children}
    </div>
  );
}

export function SentimentBadge({ label }) {
  const cls =
    label === "Positive" ? "pos" : label === "Negative" ? "neg" : "neu";
  return <span className={`badge ${cls}`}>{label}</span>;
}

// CSS-based tag/word cloud sized + colored by weight (0..1)
export function WordCloud({ words }) {
  const palette = ["#f0883e", "#58a6ff", "#3fb950", "#d2a8ff", "#ec6a5e", "#e3b341"];
  return (
    <div className="wordcloud">
      {words.map((w, i) => {
        const size = 13 + w.weight * 26;
        return (
          <span
            key={w.word}
            style={{ fontSize: `${size}px`, color: palette[i % palette.length] }}
            title={`weight ${w.weight}`}
          >
            {w.word}
          </span>
        );
      })}
    </div>
  );
}

export const CHART_COLORS = [
  "#f0883e",
  "#58a6ff",
  "#3fb950",
  "#d2a8ff",
  "#ec6a5e",
  "#e3b341",
];

export const SENTIMENT_COLORS = {
  Positive: "#3fb950",
  Neutral: "#8b949e",
  Negative: "#f85149",
};
