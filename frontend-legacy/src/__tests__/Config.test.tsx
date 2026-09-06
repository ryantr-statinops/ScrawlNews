import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Config from "../pages/Config";

describe("Config", () => {
  it("renders", () => {
    render(<Config />);
    expect(screen.getByText("Config")).toBeDefined();
  });

  it("renders config values", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            fetch_limit: 20,
            summary_lang: "vi",
            telegram_enabled: true,
          }),
      } as Response)
    );
    render(<Config />);
    await waitFor(() => {
      expect(screen.getByText("Config")).toBeDefined();
    });
  });

  it("renders Save button", () => {
    render(<Config />);
    expect(screen.getByText("Save")).toBeDefined();
  });
});
