import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Health from "../pages/Health";

describe("Health", () => {
  it("renders", () => {
    render(<Health />);
    expect(screen.getByText("System Health")).toBeDefined();
  });

  it("renders health status", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            status: "ok",
            db: "ok",
            redis: "ok",
          }),
      } as Response)
    );
    render(<Health />);
    await waitFor(() => {
      expect(screen.getByText("System Health")).toBeDefined();
    });
  });

  it("renders logs SSE section", () => {
    render(<Health />);
    expect(screen.getByText("Logs SSE")).toBeDefined();
  });
});
