import { afterEach, describe, expect, it } from "vitest";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { useThemeStore } from "../stores/themeStore";
import { useUiStore } from "../stores/uiStore";
import { StatusBadge } from "../components/ui/StatusBadge";
import { MarkdownContent } from "../components/ui/MarkdownContent";
import { theme } from "../theme";

function Controls() {
  const { colorScheme, toggle } = useThemeStore();
  const { sidebarCollapsed, toggleSidebar } = useUiStore();
  return <><span>Theme: {colorScheme}</span><button onClick={toggle}>Switch theme</button><span>Sidebar: {sidebarCollapsed ? "collapsed" : "expanded"}</span><button onClick={toggleSidebar}>Switch sidebar</button></>;
}
afterEach(() => { act(() => { useThemeStore.getState().set("dark"); useUiStore.setState({ sidebarCollapsed: false }); }); localStorage.clear(); });

describe("User preferences", () => {
  it("toggles theme persistently across a remount and keeps sidebar state local", () => {
    const first = render(<Controls />);
    expect(screen.getByText("Theme: dark")).toBeInTheDocument();
    expect(screen.getByText("Sidebar: expanded")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Switch theme" }));
    fireEvent.click(screen.getByRole("button", { name: "Switch sidebar" }));
    expect(screen.getByText("Theme: light")).toBeInTheDocument();
    expect(screen.getByText("Sidebar: collapsed")).toBeInTheDocument();
    first.unmount();
    expect(JSON.parse(localStorage.getItem("scrawlnews-theme") ?? "null")).toMatchObject({ state: { colorScheme: "light" } });
    act(() => { useThemeStore.persist.rehydrate(); });
    render(<Controls />);
    expect(screen.getByText("Theme: light")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Switch theme" }));
    fireEvent.click(screen.getByRole("button", { name: "Switch sidebar" }));
    expect(screen.getByText("Theme: dark")).toBeInTheDocument();
    expect(screen.getByText("Sidebar: expanded")).toBeInTheDocument();
  });
});

describe("Shared content", () => {
  it("communicates run progress and outcomes with distinct badge labels", () => {
    render(<MantineProvider theme={theme}><StatusBadge status="pending" /><StatusBadge status="running" /><StatusBadge status="success" /><StatusBadge status="failed" /></MantineProvider>);
    expect(screen.getByText("pending")).toBeInTheDocument();
    expect(screen.getByText("running")).toBeInTheDocument();
    expect(screen.getByText("success")).toBeInTheDocument();
    expect(screen.getByText("failed")).toBeInTheDocument();
  });

  it("renders formatted safe markdown without executing raw HTML or unsafe links", () => {
    const view = render(<MarkdownContent content={'## Headline\n\n- **Important**\n\n[Trusted](https://example.com/story) [Unsafe](javascript:alert(1))\n\n<script>window.infected=true</script>'} />);
    expect(screen.getByRole("heading", { name: "Headline" })).toBeInTheDocument();
    expect(screen.getByText("Important").tagName).toBe("STRONG");
    expect(screen.getByRole("link", { name: "Trusted" })).toHaveAttribute("href", "https://example.com/story");
    expect(screen.getByRole("link", { name: "Trusted" })).toHaveAttribute("rel", "noreferrer noopener");
    expect(screen.getByRole("link", { name: "Trusted" })).toHaveAttribute("target", "_blank");
    expect(screen.queryByRole("link", { name: "Unsafe" })).not.toBeInTheDocument();
    expect(view.container.querySelector("script")).toBeNull();
  });
});
