import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getTopics } from "../api.js";
import {
  CHART_COLORS,
  ChartCard,
  ErrorBox,
  Loading,
  WordCloud,
  useFetch,
} from "../components/common.jsx";

export default function Topics() {
  const { data, error } = useFetch(getTopics);
  if (error) return <ErrorBox message={error} />;
  if (!data) return <Loading />;

  const sizeData = data.sizes.map((s) => ({
    name: `Topic ${s.id + 1}`,
    label: s.label,
    count: s.count,
    percentage: s.percentage,
  }));

  return (
    <>
      <h1>Topic Modelling</h1>
      <p className="subtitle">
        Latent Dirichlet Allocation (LDA) uncovered six recurring themes across
        the corpus.
      </p>

      <ChartCard
        title="Topic distribution"
        hint="How many documents fall under each dominant topic."
      >
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={sizeData} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a313c" />
            <XAxis dataKey="name" stroke="#8b949e" fontSize={12} />
            <YAxis stroke="#8b949e" fontSize={12} />
            <Tooltip
              contentStyle={{ background: "#161b22", border: "1px solid #2a313c", borderRadius: 8 }}
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
              formatter={(v, _n, p) => [`${v} docs (${p.payload.percentage}%)`, p.payload.label]}
            />
            <Bar dataKey="count" radius={[6, 6, 0, 0]}>
              {sizeData.map((_, i) => (
                <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard
        title="Topics by source"
        hint="How each platform's discourse distributes across the topics."
      >
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={data.by_source} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a313c" />
            <XAxis dataKey="source" stroke="#8b949e" fontSize={12} />
            <YAxis stroke="#8b949e" fontSize={12} />
            <Tooltip
              contentStyle={{ background: "#161b22", border: "1px solid #2a313c", borderRadius: 8 }}
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            {data.topic_labels.map((label, i) => (
              <Bar
                key={label}
                dataKey={label}
                stackId="a"
                fill={CHART_COLORS[i % CHART_COLORS.length]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <h2>The six topics</h2>
      <div className="grid cols-2">
        {data.topics.map((t) => (
          <div
            className="topic-card"
            key={t.id}
            style={{ borderLeftColor: CHART_COLORS[t.id % CHART_COLORS.length] }}
          >
            <div className="topic-num">Topic {t.id + 1}</div>
            <h3>{t.label}</h3>
            <WordCloud words={t.keywords.slice(0, 18)} />
          </div>
        ))}
      </div>
    </>
  );
}
