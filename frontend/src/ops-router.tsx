import { createRouter, createRootRoute, createRoute, Outlet } from "@tanstack/react-router";
import { OpsShell } from "./components/layout/OpsShell";
import { RunsPage } from "./routes/runs";
import { HealthPage } from "./routes/health";

function Placeholder({ title }: { title: string }) { return <div><h1>{title}</h1><p>Operations workspace is being migrated.</p></div>; }
const rootRoute = createRootRoute({ component: () => <OpsShell><Outlet /></OpsShell> });
const route = (path: string, component: () => JSX.Element) => createRoute({ getParentRoute: () => rootRoute, path, component });
const routeTree = rootRoute.addChildren([
  route("/", () => <Placeholder title="Operations overview" />),
  route("/runs", RunsPage),
  route("/sources", () => <Placeholder title="Sources" />),
  route("/health", HealthPage),
  route("/telemetry", () => <Placeholder title="Telemetry" />),
  route("/failures", () => <Placeholder title="Failures" />),
  route("/orchestrator", () => <Placeholder title="Orchestrator" />),
]);
export const opsRouter = createRouter({ routeTree });
