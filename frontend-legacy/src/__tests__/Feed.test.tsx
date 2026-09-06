import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Feed from "../pages/Feed";

describe("Feed", () => {
  it("renders", () => {
    render(<Feed />);
    expect(screen.getByText("Feed")).toBeDefined();
  });

  it("renders count label", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ count: 0, articles: [] }),
      } as Response)
    );
    render(<Feed />);
    await waitFor(() => {
      expect(screen.getByText(/Count:/)).toBeDefined();
    });
  });

  it("renders article list when data available", async () => {
    const mockArticles = [
      { id: "1", title: "Test Article", url: "https://example.com" },
    ];
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ count: 1, articles: mockArticles }),
      } as Response)
    );
    render(<Feed />);
    await waitFor(() => {
      expect(screen.getByText("Test Article")).toBeDefined();
    });
  });

  it("handles empty articles array", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ count: 0, articles: [] }),
      } as Response)
    );
    render(<Feed />);
    await waitFor(() => {
      expect(screen.getByText(/Count: 0/)).toBeDefined();
    });
  });
});
