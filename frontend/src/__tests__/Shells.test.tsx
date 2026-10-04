import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { AppShell } from "../components/layout/AppShell";
import { ClientShell } from "../components/layout/ClientShell";
import { OpsShell } from "../components/layout/OpsShell";
import { useThemeStore } from "../stores/themeStore";
import { theme } from "../theme";

interface RouterStateShape {
  location: { pathname: string };
}

vi.mock("@tanstack/react-router", () => ({
  Link: ({
    to,
    label,
    children,
    ...rest
  }: {
    to: string;
    label?: string;
    children?: React.ReactNode;
  }) => (
    <a href={to} {...rest}>
      {label ?? children}
    </a>
  ),
  useRouterState: ({
    select,
  }: {
    select: (state: RouterStateShape) => unknown;
  }) => select({ location: { pathname: window.location.pathname } }),
}));

afterEach(() => {
  cleanup();
  useThemeStore.getState().set("dark");
});

function renderShell(ui: React.ReactElement, path: string) {
  window.history.replaceState(null, "", path);
  return render(<MantineProvider theme={theme}>{ui}</MantineProvider>);
}

function navLink(label: string) {
  return screen.getByText(label).closest("a");
}

describe("application shells", () => {
  it("marks the nav entry matching the current path and renders page content", () => {
    renderShell(<AppShell><p>page body</p></AppShell>, "/delivery");
    const entries: Array<[string, string]> = [
      ["Feed", "/"],
      ["Summaries", "/summaries"],
      ["Runs", "/runs"],
      ["Delivery", "/delivery"],
      ["Analytics", "/analytics"],
      ["Settings", "/settings"],
      ["Agent", "/agent"],
    ];
    for (const [label, href] of entries) expect(navLink(label)).toHaveAttribute("href", href);
    expect(navLink("Delivery")).toHaveAttribute("data-active", "true");
    expect(navLink("Runs")).not.toHaveAttribute("data-active");
    expect(screen.getByText("page body")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "ScrawlNews" })).toBeInTheDocument();
  });

  it("lists every operations entry and activates the current ops route", () => {
    renderShell(<OpsShell><p>ops body</p></OpsShell>, "/health");
    const entries: Array<[string, string]> = [
      ["Overview", "/"],
      ["Runs", "/runs"],
      ["Sources", "/sources"],
      ["Health", "/health"],
      ["Telemetry", "/telemetry"],
      ["Failures", "/failures"],
      ["Orchestrator", "/orchestrator"],
    ];
    for (const [label, href] of entries) expect(navLink(label)).toHaveAttribute("href", href);
    expect(navLink("Health")).toHaveAttribute("data-active", "true");
    expect(navLink("Runs")).not.toHaveAttribute("data-active");
    expect(screen.getByRole("heading", { name: "ScrawlNews Ops" })).toBeInTheDocument();
    expect(screen.getByText("ops body")).toBeInTheDocument();
  });

  it("exposes the client feed navigation and activates the digest entry", () => {
    renderShell(<ClientShell><p>client body</p></ClientShell>, "/summaries");
    const entries: Array<[string, string]> = [
      ["Feed", "/"],
      ["Digests", "/summaries"],
      ["Telegram", "/delivery"],
      ["Insights", "/analytics"],
      ["Settings", "/settings"],
      ["Assistant", "/agent"],
    ];
    for (const [label, href] of entries) expect(navLink(label)).toHaveAttribute("href", href);
    expect(navLink("Digests")).toHaveAttribute("data-active", "true");
    expect(navLink("Feed")).not.toHaveAttribute("data-active");
    expect(screen.getByText("client body")).toBeInTheDocument();
  });

  it("flips the persisted color scheme from the header toggle in both directions", () => {
    renderShell(<ClientShell><p>body</p></ClientShell>, "/");
    expect(useThemeStore.getState().colorScheme).toBe("dark");
    const toggle = screen.getByRole("button", { name: "Toggle theme" });
    expect(toggle.querySelector(".lucide-sun")).not.toBeNull();

    fireEvent.click(toggle);
    expect(useThemeStore.getState().colorScheme).toBe("light");
    expect(window.localStorage.getItem("scrawlnews-theme")).toContain("light");
    expect(screen.getByRole("button", { name: "Toggle theme" }).querySelector(".lucide-moon")).not.toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Toggle theme" }));
    expect(useThemeStore.getState().colorScheme).toBe("dark");
    expect(window.localStorage.getItem("scrawlnews-theme")).toContain("dark");
  });
});
