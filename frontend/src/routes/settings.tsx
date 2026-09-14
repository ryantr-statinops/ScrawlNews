import { Stack, Title } from "@mantine/core";
import { ConfigPage } from "./config";

export function SettingsPage() {
  return (
    <Stack gap="xl">
      <div>
        <Title order={2} mb="md">Settings</Title>
        <ConfigPage />
      </div>
    </Stack>
  );
}
