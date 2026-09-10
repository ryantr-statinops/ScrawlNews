import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { MarkdownContent } from "../components/ui/MarkdownContent";
import { AgentMockPanel } from "../features/feed/AgentMockPanel";
import { theme } from "../theme";

describe("Feed workspace", () => {
  it("renders GFM markdown and does not render unsafe HTML", () => {
    const { container } = render(<MantineProvider theme={theme}><MarkdownContent content={"## Briefing\n\n- **News**\n\n<script>alert('x')</script>"} /></MantineProvider>);
    expect(screen.getByRole("heading", { name: "Briefing" })).toBeDefined();
    expect(screen.getByText("News")).toBeDefined();
    expect(container.querySelector("script")).toBeNull();
  });

  it("starts the agent mock in ready state", () => {
    render(<MantineProvider theme={theme}><AgentMockPanel /></MantineProvider>);
    expect(screen.getByText("Ready · mock mode")).toBeDefined();
    expect(screen.getByLabelText("Message agent")).toBeDefined();
  });
});
