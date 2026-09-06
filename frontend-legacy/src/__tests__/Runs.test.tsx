import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Runs from "../pages/Runs";

describe("Runs", () => {
  it("renders", () => {
    render(<Runs />);
    expect(screen.getByText("Runs")).toBeDefined();
  });

  it("renders Run Now button", () => {
    render(<Runs />);
    expect(screen.getByText("Run Now")).toBeDefined();
  });

  it("renders runs list", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ runs: [] }),
      } as Response)
    );
    render(<Runs />);
    await waitFor(() => {
      expect(screen.getByText("Runs")).toBeDefined();
    });
  });
});
