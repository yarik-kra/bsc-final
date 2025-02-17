import React, { useState, useEffect } from "react";
import { NavLink } from "react-router-dom";
import "../styles/index.css";
import logo from "../images/logo.png";

function Sidebar({ searchCompleted }) {
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem("dark-mode") === "enabled"
  );

  useEffect(() => {
    document.body.classList.toggle("dark-mode", darkMode);
    localStorage.setItem("dark-mode", darkMode ? "enabled" : "disabled");
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const sidebarClass = searchCompleted ? "sidebar sidebar-expanded" : "sidebar sidebar-collapsed";

  const linkClass = searchCompleted ? "slide-in" : "slide-offscreen";

  return (
    <aside>
        <div className="toggle">
          <div className="logo">
            <img src={logo} alt="SentiTech Logo" />
            <h2>Senti<span className="tech">Tech</span></h2>
          </div>
        </div>
      <div className={sidebarClass}>
        <NavLink to="/get-started">
          <span className="material-symbols-outlined">home</span>
          <h3>Get Started</h3>
        </NavLink>
        <div className="new-tabs-container">
          <NavLink to="/feature-sentiment-analysis" className={linkClass}>
            <span className="material-symbols-outlined">sort</span>
            <h3>Feature Sentiment Analysis</h3>
          </NavLink>
          <NavLink to="/emotion-insights" className={linkClass}>
            <span className="material-symbols-outlined">emoji_language</span>
            <h3>Emotion Insights</h3>
          </NavLink>
          <NavLink to="/summarization" className={linkClass}>
            <span className="material-symbols-outlined">summarize</span>
            <h3>Summarization</h3>
          </NavLink>
          <NavLink to="/comparison-tool" className={linkClass}>
            <span className="material-symbols-outlined">text_compare</span>
            <h3>Comparison Tool</h3>
          </NavLink>
          <NavLink to="/advice" className={linkClass}>
            <span className="material-symbols-outlined">lightbulb</span>
            <h3>Advice</h3>
          </NavLink>
        </div>

        <button id="dark-mode-toggle" onClick={toggleDarkMode}>
          <span className="material-symbols-outlined">
            {darkMode ? "light_mode" : "dark_mode"}
          </span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
