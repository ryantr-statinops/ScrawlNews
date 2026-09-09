import { Stack, Title } from "@mantine/core";
import { ConfigPage } from "./config";
import { HealthPage } from "./health";

export function SettingsPage() {
  return (
    <Stack gap="xl">
      <div>
        <Title order={2} mb="md">Settings</Title>
        <ConfigPage />
      </div>
      <div>
        <Title order={2} mb="md">System health</Title>
        <HealthPage />
      </div>
    </Stack>
  );
}
