import React, { useEffect, useState } from "react";
import "../styles/feature-sentiment.css";

const FeatureSentiment = () => {
    const [sentimentData, setSentimentData] = useState(null);

    useEffect(() => {
        fetch("http://localhost:8000/api/results")
            .then(response => response.json())
            .then(data => setSentimentData(data))
            .catch(error => console.error("Error fetching sentiment data:", error));
    }, []);

    return (
        <main>
            <h1>Feature Sentiment Analysis</h1>
            <div className="main-box">
                {sentimentData ? (
                    <>
                        <p>
                            This section provides a detailed sentiment breakdown based on the
                            features mentioned of the product you have entered, helping you
                            understand how users feel about different aspects of{" "}
                            {sentimentData.product_name}.
                        </p>
                        <h2>Overview</h2>
                        <p>✅ Positive Sentiment: {sentimentData.positive_percentage}% of user opinions expressed satisfaction.</p>
                        <p>❌ Negative Sentiment: {sentimentData.negative_percentage}% of user opinions highlighted concerns.</p>
                        <p>➖ Neutral Sentiment: {sentimentData.neutral_percentage}% of user opinions provided balanced feedback.</p>
                        <h2>Praised Features</h2>
                        <ul>
                            {sentimentData.praised_features.length > 0 ? (
                                sentimentData.praised_features.map((feature, index) => (
                                    <p>⭐ {feature}</p>
                                ))
                            ) : (
                                <p>No specific features were highly praised.</p>
                            )}
                        </ul>
                    </>
                ) : (
                    <p>Loading sentiment data...</p>
                )}
            </div>
        </main>
    );
};

export default FeatureSentiment;