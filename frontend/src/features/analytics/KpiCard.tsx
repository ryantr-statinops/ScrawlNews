import { Card, Group, Text, ThemeIcon, Title } from "@mantine/core";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import type { ComparisonMetric } from "./types";

interface Props {
  label: string;
  metric: ComparisonMetric;
  format?: (value: number) => string;
  inverse?: boolean;
  onClick?: () => void;
}

const defaultFormat = (value: number) => new Intl.NumberFormat().format(value);

export function KpiCard({ label, metric, format = defaultFormat, inverse = false, onClick }: Props) {
  const improved = inverse ? metric.delta < 0 : metric.delta > 0;
  const changed = metric.delta !== 0;
  const color = !changed ? "gray" : improved ? "teal" : "red";
  const Icon = !changed ? Minus : metric.delta > 0 ? ArrowUpRight : ArrowDownRight;
  const delta = !changed ? "No change" : metric.delta_percent === null ? "New baseline" : `${Math.abs(metric.delta_percent)}%`;

  return (
    <Card
      withBorder
      padding="lg"
      onClick={onClick}
      role={onClick ? "button" : undefined}
      aria-label={onClick ? `Inspect ${label}` : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(event) => {
        if (onClick && (event.key === "Enter" || event.key === " ")) {
          event.preventDefault();
          onClick();
        }
      }}
      style={{ cursor: onClick ? "pointer" : undefined }}
    >
      <Text size="xs" tt="uppercase" fw={700} c="dimmed">{label}</Text>
      <Group justify="space-between" align="end" mt={6}>
        <Title order={2}>{format(metric.current)}</Title>
        <Group gap={5}>
          <ThemeIcon color={color} variant="light" size="sm"><Icon size={14} /></ThemeIcon>
          <Text size="xs" c={color} fw={600}>{delta}</Text>
        </Group>
      </Group>
      <Text size="xs" c="dimmed" mt={4}>Previous: {format(metric.previous)}</Text>
    </Card>
  );
}
