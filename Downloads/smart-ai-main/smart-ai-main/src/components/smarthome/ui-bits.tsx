import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { PlanStatus, SensorEvent } from "@/lib/smarthome/types";
import { DoorOpen, Lightbulb, Plug, Radar, Thermometer, ToggleRight } from "lucide-react";

export function ConfidenceBar({ value, label }: { value: number; label?: string }) {
  const pct = Math.round(value * 100);
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{label ?? "Confidence"}</span>
        <span className="font-medium text-foreground">{pct}%</span>
      </div>
      <div
        className="h-2 w-full overflow-hidden rounded-full bg-muted"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

const statusStyles: Record<PlanStatus, string> = {
  COMPLETED: "bg-success/15 text-success border-success/30",
  DELAYED: "bg-warning/20 text-warning-foreground border-warning/40",
  "TEMPORARY DEVIATION": "bg-accent text-accent-foreground border-border",
  DEVIATED: "bg-destructive/10 text-destructive border-destructive/30",
  "NOT CONFIRMED": "bg-muted text-muted-foreground border-border",
  UPCOMING: "bg-primary/10 text-primary border-primary/25",
};

export function StatusBadge({ status }: { status: PlanStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-medium tracking-wide",
        statusStyles[status],
      )}
    >
      {status}
    </span>
  );
}

export function RoomChip({ room }: { room: string }) {
  return (
    <Badge variant="secondary" className="rounded-full font-normal">
      {room}
    </Badge>
  );
}

const sensorIcon = {
  motion: Radar,
  door: DoorOpen,
  light: Lightbulb,
  temperature: Thermometer,
  appliance: ToggleRight,
  plug: Plug,
};

export function SensorChip({ event }: { event: SensorEvent }) {
  const Icon = sensorIcon[event.sensorType];
  const val =
    event.sensorType === "temperature"
      ? `${event.value.toFixed(1)}${event.unit ?? ""}`
      : event.sensorType === "plug"
        ? `${Math.round(event.value)}W`
        : event.value > 0
          ? "ON"
          : "OFF";
  return (
    <div className="flex items-center gap-2 rounded-lg border bg-card px-2.5 py-1.5 text-xs">
      <Icon className="size-3.5 text-primary" />
      <span className="font-medium">{event.sensorId}</span>
      <span className="text-muted-foreground">{val}</span>
    </div>
  );
}

export function timeAgo(ts: number) {
  const diff = Math.max(0, Date.now() - ts);
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export function clockTime(ts: number) {
  return new Date(ts).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

export function SectionHeader({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function LoadingCards({ count = 4 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-32 animate-pulse rounded-xl border bg-card" />
      ))}
    </div>
  );
}
