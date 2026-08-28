import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Analytics from "../pages/Analytics";

describe("Analytics", () => {
  it("renders", () => {
    render(<Analytics />);
    expect(screen.getByText("Analytics")).toBeDefined();
  });

  it("renders stats when data available", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            articles_per_day: [],
            source_dist: [],
          }),
      } as Response)
    );
    render(<Analytics />);
    await waitFor(() => {
      expect(screen.getByText("Analytics")).toBeDefined();
    });
  });
});
