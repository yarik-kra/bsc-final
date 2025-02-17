import React, { useState } from "react";
import "../styles/get-started.css";

function GetStarted({ setSearchCompleted }) {
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    const input = document.getElementById("product-input");
    if (!input) return;
    const productName = input.value.trim();
    if (!productName) {
      alert("Please enter a product name.");
      return;
    }
    setLoading(true);
    input.value = "";
    try {
      const response = await fetch("http://127.0.0.1:8000/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product: productName }),
      });
      if (response.ok) {
        console.log("Search completed!");
        setSearchCompleted(true);
      }
    } catch (error) {
      console.error("Fetch error:", error);
    }
    setLoading(false);
  };

  return (
    <main>
      <h1>Get Started</h1>
      <div className="welcome">
        <h2>Welcome to SentiTech</h2>
        <p>
          Welcome to SentiTech, your intelligent tool for uncovering how people truly feel about tech products across online marketplaces and forums. Whether you're a tech enthusiast, a savvy consumer, or a company looking for market insights, our platform is designed to give you real-time sentiment analysis and feature-specific opinions at your fingertips.
        </p>
      </div>
      {!loading ? (
        <div className="search">
          <h2>Please enter the product you would like to analyze:</h2>
          <div className="search-container">
            <input type="text" id="product-input" placeholder="Enter product name..." />
            <button id="search-btn" className="green-button" onClick={handleSearch}>
              <span className="material-symbols-outlined">search</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Fetching product data, please wait...</p>
        </div>
      )}
    </main>
  );
}

export default GetStarted;
