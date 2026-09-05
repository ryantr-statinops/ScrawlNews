import { Alert } from "@mantine/core";

export function ErrorState({ message }: { message: string }) {
  return (
    <Alert color="red" title="Error">
      {message}
    </Alert>
  );
}
