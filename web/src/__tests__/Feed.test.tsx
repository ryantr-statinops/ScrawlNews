import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Feed from "../pages/Feed";

describe("Feed", () => {
  it("renders", () => {
    render(<Feed />);
    expect(screen.getByText("Feed")).toBeDefined();
  });
});
