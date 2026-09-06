import { Badge } from "@mantine/core";
import type { PipelineRun } from "../../types/api";

const colorMap: Record<PipelineRun["status"], string> = {
  pending: "yellow",
  running: "blue",
  success: "green",
  failed: "red",
};

export function StatusBadge({ status }: { status: PipelineRun["status"] }) {
  return <Badge color={colorMap[status]}>{status}</Badge>;
}
