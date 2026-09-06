import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";

describe("Shared Components", () => {
  it("placeholder component test", () => {
    const TestComponent = () => <div data-testid="test">Test</div>;
    render(<TestComponent />);
    expect(screen.getByTestId("test").textContent).toBe("Test");
  });
});
