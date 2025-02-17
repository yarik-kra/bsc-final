import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes, Outlet, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar.js";
import GetStarted from "./components/GetStarted.js";
import FeatureSentiment from "./components/FeatureSentiment.js";
import EmotionInsights from "./components/EmotionInsights.js";
import Summarization from "./components/Summarization.js";
import ComparisonTool from "./components/ComparisonTool.js";
import Advice from "./components/Advice.js";
import "./styles/index.css";

// Layout component: Sidebar always present, content updates dynamically
function Layout({ searchCompleted }) {
  return (
    <div className="container">
      <Sidebar searchCompleted={searchCompleted} />
      <main id="main-content">
        <Outlet />
      </main>
    </div>
  );
}

function App() {
  // Define searchCompleted state and setter
  const [searchCompleted, setSearchCompleted] = useState(false);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/get-started" replace />} />
        <Route path="/" element={<Layout searchCompleted={searchCompleted} />}>
          <Route path="get-started" element={<GetStarted setSearchCompleted={setSearchCompleted} />} />
          <Route path="feature-sentiment-analysis" element={<FeatureSentiment />} />
          <Route path="emotion-insights" element={<EmotionInsights />} />
          <Route path="summarization" element={<Summarization />} />
          <Route path="comparison-tool" element={<ComparisonTool />} />
          <Route path="advice" element={<Advice />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
