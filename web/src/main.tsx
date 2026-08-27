import React from "react";
import ReactDOM from "react-dom/client";
import Feed from "./pages/Feed";
import Runs from "./pages/Runs";
import Config from "./pages/Config";

function App() {
  return (
    <div style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>ScrawlNews Dashboard</h1>
      <Feed />
      <Runs />
      <Config />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
