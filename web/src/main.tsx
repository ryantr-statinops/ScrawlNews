import React from "react";
import ReactDOM from "react-dom/client";
import Feed from "./pages/Feed";
import Runs from "./pages/Runs";
import Config from "./pages/Config";
import Summaries from "./pages/Summaries";
import Delivery from "./pages/Delivery";
import Health from "./pages/Health";
import Analytics from "./pages/Analytics";

function App() {
  return (
    <div style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>ScrawlNews Dashboard</h1>
      <Feed />
      <Summaries />
      <Runs />
      <Delivery />
      <Health />
      <Analytics />
      <Config />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
