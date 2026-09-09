import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { KpiCard } from "../features/analytics/KpiCard";
import { theme } from "../theme";

describe("Analytics KpiCard", () => {
  it("renders the previous-period comparison and supports keyboard drill-down", () => {
    const inspect = vi.fn();
    render(
      <MantineProvider theme={theme}>
        <KpiCard
          label="Pipeline success"
          metric={{ current: 95, previous: 80, delta: 15, delta_percent: 18.8 }}
          format={(value) => `${value}%`}
          onClick={inspect}
        />
      </MantineProvider>,
    );

    expect(screen.getByText("95%")).toBeInTheDocument();
    expect(screen.getByText("Previous: 80%")).toBeInTheDocument();
    fireEvent.keyDown(screen.getByRole("button", { name: "Inspect Pipeline success" }), {
      key: "Enter",
    });
    expect(inspect).toHaveBeenCalledOnce();
  });
});
