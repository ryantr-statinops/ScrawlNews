import React from "react";
import ReactDOM from "react-dom/client";
import { MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "@tanstack/react-router";
import { theme } from "./theme";
import { router } from "./router";
import { opsRouter } from "./ops-router";
import { useThemeStore } from "./stores/themeStore";
import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";

const queryClient = new QueryClient();

function InnerApp() {
  const colorScheme = useThemeStore((s) => s.colorScheme);
  const isOpsApp = import.meta.env.VITE_APP === "ops" || import.meta.env.MODE === "ops";
  const activeRouter = isOpsApp ? opsRouter : router;
  return (
    <MantineProvider theme={theme} forceColorScheme={colorScheme}>
      <Notifications />
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={activeRouter} />
      </QueryClientProvider>
    </MantineProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <InnerApp />
  </React.StrictMode>,
);
