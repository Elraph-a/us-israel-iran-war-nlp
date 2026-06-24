import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getOverview } from "../api.js";
import {
  CHART_COLORS,
  ChartCard,
  ErrorBox,
  Loading,
  StatCard,
  useFetch,
} from "../components/common.jsx";

export default function Overview() {
  const { data, error } = useFetch(getOverview);
  if (error) return <ErrorBox message={error} />;
  if (!data) return <Loading />;

  const sources = [...data.sources].sort((a, b) => b.count - a.count);

  return (
    <>
      <section className="hero">
        <div className="eyebrow">NLP Project</div>
        <h1>US / Israel–Iran War: Online Discourse Analysis</h1>
        <p className="subtitle">{data.scope}</p>
        <p className="muted" style={{ maxWidth: 720 }}>
          An end-to-end NLP pipeline — topic modelling and sentiment analysis —
          applied to {data.total_documents.toLocaleString()} documents gathered
          from news outlets and social media. Explore the findings, or run the
          models live on your own text in the Analyzer.
        </p>
      </section>

      <div className="grid cols-3">
        <StatCard value={data.total_documents.toLocaleString()} label="Documents analyzed" />
        <StatCard value={data.num_sources} label="Data sources" />
        <StatCard value={data.num_topics} label="Topics discovered" />
      </div>

      <h2>Documents by Source</h2>
      <ChartCard
        title="Where the discourse came from"
        hint="Number of collected documents per platform / outlet."
      >
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={sources} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a313c" />
            <XAxis dataKey="source" stroke="#8b949e" fontSize={12} />
            <YAxis stroke="#8b949e" fontSize={12} />
            <Tooltip
              contentStyle={{ background: "#161b22", border: "1px solid #2a313c", borderRadius: 8 }}
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
            />
            <Bar dataKey="count" radius={[6, 6, 0, 0]}>
              {sources.map((_, i) => (
                <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <h2>Methodology at a glance</h2>
      <div className="card">
        <ul className="clean">
          {data.methods.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      </div>
    </>
  );
}
