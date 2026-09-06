import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { FeedTable } from "../features/feed/FeedTable";
import { theme } from "../theme";

describe("FeedTable", () => {
  it("renders articles", () => {
    render(
      <MantineProvider theme={theme}>
        <FeedTable
          articles={[
            { id: "a1", title: "Hello", url: "http://a.com", source: "BBC", fetched_at: null, summarized: 0 },
          ]}
        />
      </MantineProvider>,
    );
    expect(screen.getByText("Hello")).toBeDefined();
  });
});
