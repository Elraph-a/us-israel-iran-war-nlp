import { NavLink, Route, Routes } from "react-router-dom";
import Overview from "./pages/Overview.jsx";
import Topics from "./pages/Topics.jsx";
import Sentiment from "./pages/Sentiment.jsx";
import Analyzer from "./pages/Analyzer.jsx";
import About from "./pages/About.jsx";

export default function App() {
  return (
    <div className="app">
      <nav className="nav">
        <div className="nav-brand">
          <span className="dot" />
          War Discourse&nbsp;NLP
        </div>
        <NavLink to="/" end>
          Overview
        </NavLink>
        <NavLink to="/topics">Topics</NavLink>
        <NavLink to="/sentiment">Sentiment</NavLink>
        <NavLink to="/analyzer">Analyzer</NavLink>
        <NavLink to="/about">About</NavLink>
      </nav>

      <main className="container">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/topics" element={<Topics />} />
          <Route path="/sentiment" element={<Sentiment />} />
          <Route path="/analyzer" element={<Analyzer />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>

      <footer className="footer">
        NLP Project · US / Israel–Iran War Discourse Analysis
      </footer>
    </div>
  );
}
