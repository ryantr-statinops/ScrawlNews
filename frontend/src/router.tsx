import { createRouter, createRootRoute, createRoute, Outlet } from "@tanstack/react-router";
import { ClientShell } from "./components/layout/ClientShell";
import { FeedPage } from "./routes/index";
import { SummariesPage } from "./routes/summaries";
import { DeliveryPage } from "./routes/delivery";
import { AnalyticsPage } from "./routes/analytics";
import { ConfigPage } from "./routes/config";
import { SettingsPage } from "./routes/settings";
import { AgentPage } from "./routes/agent";

const rootRoute = createRootRoute({
  component: () => (
    <ClientShell>
      <Outlet />
    </ClientShell>
  ),
});

function withRoot(path: string, component: () => JSX.Element) {
  return createRoute({
    getParentRoute: () => rootRoute,
    path,
    component,
  });
}

const indexRoute = withRoot("/", FeedPage);
const summariesRoute = withRoot("/summaries", SummariesPage);
const deliveryRoute = withRoot("/delivery", DeliveryPage);
const analyticsRoute = withRoot("/analytics", AnalyticsPage);
const configRoute = withRoot("/config", ConfigPage);
const settingsRoute = withRoot("/settings", SettingsPage);
const agentRoute = withRoot("/agent", AgentPage);

const routeTree = rootRoute.addChildren([
  indexRoute,
  summariesRoute,
  deliveryRoute,
  analyticsRoute,
  configRoute,
  settingsRoute,
  agentRoute,
]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
