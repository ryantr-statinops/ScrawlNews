import { useState } from "react";
import { ActionIcon, Button, Card, Group, Text, TextInput } from "@mantine/core";
import { ChevronDown, ChevronUp, Send } from "lucide-react";
import "./AgentMockPanel.css";

export function AgentMockPanel() {
  const [expanded, setExpanded] = useState(true);
  const [floating, setFloating] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState(["I can help you inspect this feed."]);

  const send = () => {
    const value = message.trim();
    if (!value) return;
    setMessages((current) => [...current, value]);
    setMessage("");
  };

  return <Card withBorder className={`agent-mock${expanded ? "" : " agent-mock--collapsed"}${floating ? " agent-mock--floating" : ""}`}>
    <Group justify="space-between">
      <div><Text fw={700}>Agent</Text><Text size="xs" c="teal">Ready · mock mode</Text></div>
      <Group gap={4}><Button variant="subtle" size="compact-xs" onClick={() => setFloating((value) => !value)}>{floating ? "Dock" : "Float"}</Button><ActionIcon variant="subtle" aria-label={expanded ? "Collapse agent" : "Expand agent"} onClick={() => setExpanded((value) => !value)}>{expanded ? <ChevronDown size={16} /> : <ChevronUp size={16} />}</ActionIcon></Group>
    </Group>
    {expanded ? <>
      <Card.Section className="agent-mock__messages" p="sm" mt="sm">
        {messages.map((item, index) => <Text key={`${item}-${index}`} size="sm" mb="xs" p="xs" bg={index === 0 ? "gray.0" : "blue.0"}>{item}</Text>)}
      </Card.Section>
      <Group gap="xs" mt="sm" wrap="nowrap"><TextInput aria-label="Message agent" placeholder="Ask the agent..." value={message} onChange={(event) => setMessage(event.currentTarget.value)} onKeyDown={(event) => event.key === "Enter" && send()} style={{ flex: 1 }} /><Button aria-label="Send message" onClick={send} px="sm"><Send size={16} /></Button></Group>
    </> : null}
  </Card>;
}
