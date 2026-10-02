import { createFileRoute, Navigate } from "@tanstack/react-router";

export const Route = createFileRoute("/evaluation")({
  component: () => <Navigate to="/" replace />,
});
