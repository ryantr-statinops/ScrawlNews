import { createRouter, createRootRoute, createRoute } from "@tanstack/react-router";
import { AppShell } from "./components/layout/AppShell";
import { FeedPage } from "./routes/index";
import { SummariesPage } from "./routes/summaries";
import { RunsPage } from "./routes/runs";
import { DeliveryPage } from "./routes/delivery";
import { AnalyticsPage } from "./routes/analytics";
import { HealthPage } from "./routes/health";
import { ConfigPage } from "./routes/config";

const rootRoute = createRootRoute({
  component: () => (
    <AppShell>
      <div id="outlet" />
    </AppShell>
  ),
});

function withRoot(path: string, component: React.ComponentType) {
  return createRoute({
    getParentRoute: () => rootRoute,
    path,
    component,
  });
}

const indexRoute = withRoot("/", FeedPage);
const summariesRoute = withRoot("/summaries", SummariesPage);
const runsRoute = withRoot("/runs", RunsPage);
const deliveryRoute = withRoot("/delivery", DeliveryPage);
const analyticsRoute = withRoot("/analytics", AnalyticsPage);
const healthRoute = withRoot("/health", HealthPage);
const configRoute = withRoot("/config", ConfigPage);

const routeTree = rootRoute.addChildren([
  indexRoute,
  summariesRoute,
  runsRoute,
  deliveryRoute,
  analyticsRoute,
  healthRoute,
  configRoute,
]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
