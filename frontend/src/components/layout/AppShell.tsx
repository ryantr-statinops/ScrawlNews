import { AppShell as MantineShell, Burger, Group, Title, ActionIcon } from "@mantine/core";
import { Sun, Moon } from "lucide-react";
import { useDisclosure } from "@mantine/hooks";
import { useThemeStore } from "../../stores/themeStore";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [opened, { toggle }] = useDisclosure();
  const { colorScheme, toggle: toggleTheme } = useThemeStore();

  return (
    <MantineShell
      header={{ height: 60 }}
      navbar={{ width: 220, breakpoint: "sm", collapsed: { mobile: !opened } }}
      padding="md"
    >
      <MantineShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <Title order={3}>ScrawlNews</Title>
          </Group>
          <ActionIcon variant="default" onClick={toggleTheme} aria-label="Toggle theme">
            {colorScheme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </ActionIcon>
        </Group>
      </MantineShell.Header>
      <MantineShell.Navbar p="md">{null}</MantineShell.Navbar>
      <MantineShell.Main>{children}</MantineShell.Main>
    </MantineShell>
  );
}
