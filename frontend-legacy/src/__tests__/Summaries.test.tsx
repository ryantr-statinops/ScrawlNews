import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Summaries from "../pages/Summaries";

describe("Summaries", () => {
  it("renders", () => {
    render(<Summaries />);
    expect(screen.getByText("Summaries")).toBeDefined();
  });

  it("renders count label", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ count: 0, summaries: [] }),
      } as Response)
    );
    render(<Summaries />);
    await waitFor(() => {
      expect(screen.getByText(/Count:/)).toBeDefined();
    });
  });

  it("renders summaries list", async () => {
    const mockSummaries = [
      { id: "s1", summary_text: "Test summary", article_id: "a1" },
    ];
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ count: 1, summaries: mockSummaries }),
      } as Response)
    );
    render(<Summaries />);
    await waitFor(() => {
      expect(screen.getByText("Test summary")).toBeDefined();
    });
  });
});
