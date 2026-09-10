import { describe, expect, it } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { MarkdownContent } from "../components/ui/MarkdownContent";
import { AgentMockPanel } from "../features/feed/AgentMockPanel";
import { DigestPanel, latestDigestsByCategory } from "../features/feed/DigestPanel";
import { FeedWorkspace } from "../features/feed/FeedWorkspace";
import { theme } from "../theme";
import type { Digest } from "../types/api";

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
    expect(screen.queryByRole("button", { name: "Float" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Dock" })).toBeNull();
  });

  it("keeps only the newest digest for each category in the rail", () => {
    const digests: Digest[] = [
      { id: "old", category: "technology", title: "Old", digest_text: "Old", article_count: 1, model_used: "model", status: "success", error: null, created_at: "2026-09-01T00:00:00Z" },
      { id: "new", category: "technology", title: "New", digest_text: "New", article_count: 2, model_used: "model", status: "success", error: null, created_at: "2026-09-02T00:00:00Z" },
      { id: "world", category: "world", title: "World", digest_text: "World", article_count: 1, model_used: "model", status: "success", error: null, created_at: "2026-09-01T00:00:00Z" },
    ];
    expect(latestDigestsByCategory(digests).map((digest) => digest.id)).toEqual(["new", "world"]);
    render(<MantineProvider theme={theme}><FeedWorkspace agent={<AgentMockPanel />} digests={<DigestPanel digests={digests} />} articles={<div>Articles</div>} /></MantineProvider>);
    expect(screen.getAllByText("New").length).toBeGreaterThan(0);
    expect(screen.queryByText("Old")).toBeNull();
  });
});
