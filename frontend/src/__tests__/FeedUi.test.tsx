import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { AgentMockPanel } from "../features/feed/AgentMockPanel";
import { ArticlePanel } from "../features/feed/ArticlePanel";
import { DigestPanel } from "../features/feed/DigestPanel";
import { FeedTable } from "../features/feed/FeedTable";
import { FeedWorkspace } from "../features/feed/FeedWorkspace";
import { theme } from "../theme";
import type { Article, Digest } from "../types/api";

const article: Article = {
  id: "a1",
  title: "Article One",
  url: "https://example.com/one",
  source: "Example",
  category: "technology",
  content: "Article content",
  fetched_at: "2026-09-10T01:00:00Z",
  published_at: "2026-09-10T00:00:00Z",
  summarized: 1,
};

const digests: Digest[] = [
  { id: "old", category: "technology", title: "Old digest", digest_text: "Old content", article_count: 1, model_used: "model", status: "success", error: null, created_at: "2026-09-09T00:00:00Z" },
  { id: "new", category: "technology", title: "Latest digest", digest_text: "## Latest\n\n- **Important**", article_count: 2, model_used: "model", status: "success", error: null, created_at: "2026-09-10T00:00:00Z" },
];

function renderWorkspace() {
  return render(
    <MantineProvider theme={theme}>
      <FeedWorkspace
        agent={<AgentMockPanel />}
        digests={<DigestPanel digests={digests} />}
        articles={<ArticlePanel total={1}><FeedTable articles={[article]} /></ArticlePanel>}
      />
    </MantineProvider>,
  );
}

describe("Feed UI", () => {
  it("renders the utility rail before the article panel", () => {
    renderWorkspace();
    const tools = screen.getByRole("region", { name: "Feed tools" });
    const articles = screen.getByRole("region", { name: "Articles" });
    expect(tools.compareDocumentPosition(articles) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(within(tools).getByText("Agent")).toBeDefined();
    expect(within(tools).getByRole("heading", { name: "Topic digests" })).toBeDefined();
    expect(within(articles).getByRole("heading", { name: "Articles" })).toBeDefined();
  });

  it("keeps Agent controls local and restores the docked state", () => {
    const { container } = renderWorkspace();
    const agent = container.querySelector(".agent-mock");
    expect(agent).not.toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Float" }));
    expect(screen.getByRole("button", { name: "Dock" })).toBeDefined();
    expect(agent?.className).toContain("agent-mock--floating");
    fireEvent.click(screen.getByRole("button", { name: "Collapse agent" }));
    expect(screen.getByRole("button", { name: "Expand agent" })).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: "Expand agent" }));
    fireEvent.change(screen.getByLabelText("Message agent"), { target: { value: "check layout" } });
    fireEvent.click(screen.getByRole("button", { name: "Send message" }));
    expect(screen.getByText("check layout")).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: "Dock" }));
    expect(screen.getByRole("button", { name: "Float" })).toBeDefined();
  });

  it("shows only the latest digest and emits the selected digest", () => {
    const onSelect = vi.fn();
    render(<MantineProvider theme={theme}><DigestPanel digests={digests} onSelect={onSelect} /></MantineProvider>);
    expect(screen.getByText("Latest digest")).toBeDefined();
    expect(screen.queryByText("Old digest")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Open digest" }));
    expect(onSelect).toHaveBeenCalledWith(digests[1]);
  });

  it("opens an article through the row selection callback", () => {
    const onSelect = vi.fn();
    render(<MantineProvider theme={theme}><FeedTable articles={[article]} onSelect={onSelect} /></MantineProvider>);
    fireEvent.click(screen.getByText("Article One"));
    expect(onSelect).toHaveBeenCalledWith(article);
  });

});
