import { AppShell as MantineShell, Burger, Group, Title, ActionIcon, NavLink } from "@mantine/core";
import { Sun, Moon } from "lucide-react";
import { useDisclosure } from "@mantine/hooks";
import { Link, useRouterState } from "@tanstack/react-router";
import { useThemeStore } from "../../stores/themeStore";

const navItems = [
  { to: "/", label: "Feed" },
  { to: "/summaries", label: "Summaries" },
  { to: "/runs", label: "Runs" },
  { to: "/delivery", label: "Delivery" },
  { to: "/analytics", label: "Analytics" },
  { to: "/settings", label: "Settings" },
  { to: "/agent", label: "Agent" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const [opened, { toggle }] = useDisclosure();
  const { colorScheme, toggle: toggleTheme } = useThemeStore();
  const pathname = useRouterState({ select: (s) => s.location.pathname });

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
      <MantineShell.Navbar p="md">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            label={item.label}
            component={Link}
            to={item.to}
            active={pathname === item.to}
          />
        ))}
      </MantineShell.Navbar>
      <MantineShell.Main>{children}</MantineShell.Main>
    </MantineShell>
  );
}
