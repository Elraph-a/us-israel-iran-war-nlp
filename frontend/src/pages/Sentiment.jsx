import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getSentiment } from "../api.js";
import {
  ChartCard,
  ErrorBox,
  Loading,
  SENTIMENT_COLORS,
  StatCard,
  useFetch,
} from "../components/common.jsx";

function distToArray(d) {
  return [
    { name: "Positive", value: d.Positive },
    { name: "Neutral", value: d.Neutral },
    { name: "Negative", value: d.Negative },
  ];
}

const axisTip = {
  contentStyle: { background: "#161b22", border: "1px solid #2a313c", borderRadius: 8 },
  cursor: { fill: "rgba(255,255,255,0.04)" },
};

export default function Sentiment() {
  const { data, error } = useFetch(getSentiment);
  if (error) return <ErrorBox message={error} />;
  if (!data) return <Loading />;

  const vader = distToArray(data.vader_distribution);
  const tb = distToArray(data.textblob_distribution);

  return (
    <>
      <h1>Sentiment Analysis</h1>
      <p className="subtitle">
        Two complementary lexicon methods — VADER and TextBlob — scored the
        emotional tone of every document.
      </p>

      <div className="grid cols-3">
        <StatCard
          value={data.vader_overall_avg}
          label="Avg VADER compound (−1 → +1)"
        />
        <StatCard
          value={data.textblob_overall_avg}
          label="Avg TextBlob polarity (−1 → +1)"
        />
        <StatCard
          value={`${(data.supervised_accuracy * 100).toFixed(1)}%`}
          label="Supervised model accuracy"
        />
      </div>

      <h2>Sentiment distribution</h2>
      <div className="grid cols-2">
        {[
          { title: "VADER", arr: vader },
          { title: "TextBlob", arr: tb },
        ].map(({ title, arr }) => (
          <ChartCard key={title} title={`${title} labels`} hint="Share of documents by sentiment.">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={arr}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  label={(e) => e.name}
                >
                  {arr.map((e) => (
                    <Cell key={e.name} fill={SENTIMENT_COLORS[e.name]} />
                  ))}
                </Pie>
                <Tooltip {...axisTip} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        ))}
      </div>

      <h2>Average sentiment by source</h2>
      <ChartCard
        title="VADER compound by platform"
        hint="Negative bars (red) lean toward negative discourse."
      >
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={data.by_source} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a313c" />
            <XAxis dataKey="source" stroke="#8b949e" fontSize={12} />
            <YAxis stroke="#8b949e" fontSize={12} />
            <Tooltip {...axisTip} />
            <Bar dataKey="vader_avg" radius={[6, 6, 0, 0]}>
              {data.by_source.map((d, i) => (
                <Cell key={i} fill={d.vader_avg >= 0 ? "#3fb950" : "#f85149"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <h2>Traditional news vs social media</h2>
      <ChartCard
        title="Tone by media type"
        hint="Average VADER compound score, news outlets vs social platforms."
      >
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data.media_comparison} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a313c" />
            <XAxis dataKey="media_type" stroke="#8b949e" fontSize={12} />
            <YAxis stroke="#8b949e" fontSize={12} />
            <Tooltip {...axisTip} />
            <Bar dataKey="vader_avg" radius={[6, 6, 0, 0]}>
              {data.media_comparison.map((d, i) => (
                <Cell key={i} fill={d.vader_avg >= 0 ? "#3fb950" : "#f85149"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <h2>Sentiment across conflict dimensions</h2>
      <ChartCard
        title="How tone varies by theme"
        hint="Documents matching keywords for each conflict dimension, scored with VADER."
      >
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={data.dimensions} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a313c" />
            <XAxis dataKey="dimension" stroke="#8b949e" fontSize={12} />
            <YAxis stroke="#8b949e" fontSize={12} />
            <Tooltip {...axisTip} />
            <Bar dataKey="vader_avg" radius={[6, 6, 0, 0]}>
              {data.dimensions.map((d, i) => (
                <Cell key={i} fill={d.vader_avg >= 0 ? "#3fb950" : "#f85149"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </>
  );
}
