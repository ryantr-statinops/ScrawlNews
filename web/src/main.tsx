import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  return (
    <div style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>ScrawlNews Dashboard</h1>
      <p>Stage 1 Foundation - placeholder. API: /api/health</p>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
