import { createTheme, type MantineColorsTuple } from "@mantine/core";

const primary: MantineColorsTuple = [
  "#EFF6FF",
  "#DBEAFE",
  "#BFDBFE",
  "#93C5FD",
  "#60A5FA",
  "#3B82F6",
  "#2563EB",
  "#1D4ED8",
  "#1E40AF",
  "#1E3A8A",
];

const accent: MantineColorsTuple = [
  "#E0F7FF",
  "#B3EDFF",
  "#80E2FF",
  "#4DD7FF",
  "#26CDFF",
  "#00C7FC",
  "#00A6D4",
  "#0085AB",
  "#006482",
  "#004359",
];

export const theme = createTheme({
  primaryColor: "primary",
  colors: { primary, accent },
  fontFamily: "Inter, system-ui, -apple-system, sans-serif",
  fontFamilyMonospace: "JetBrains Mono, monospace",
  defaultRadius: "md",
  primaryShade: { light: 6, dark: 4 },
});
