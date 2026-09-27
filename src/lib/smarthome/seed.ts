// Deterministic demo seed data. Built lazily (never at module scope) so the
// worker runtime and SSR stay happy.

import type {
  ActivityHistoryEntry,
  Appliance,
  Profile,
  Room,
  ScheduleTask,
  SensorEvent,
  ActivityLabel,
} from "./types";

function rng(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 0xffffffff;
  };
}

export function seedTasks(): ScheduleTask[] {
  return [
    { id: "t1", time: "07:00", task: "Morning shower", activity: "Showering", room: "Bathroom", durationMin: 20, repeat: "daily" },
    { id: "t2", time: "08:00", task: "Breakfast", activity: "Breakfast", room: "Kitchen", durationMin: 30, repeat: "daily" },
    { id: "t3", time: "10:00", task: "Study session", activity: "Study", room: "Study", durationMin: 120, repeat: "weekdays" },
    { id: "t4", time: "13:00", task: "Lunch", activity: "Lunch", room: "Kitchen", durationMin: 40, repeat: "daily" },
    { id: "t5", time: "15:00", task: "Deep work", activity: "Study", room: "Study", durationMin: 90, repeat: "weekdays" },
    { id: "t6", time: "18:00", task: "Exercise", activity: "Exercise", room: "Gym", durationMin: 45, repeat: "daily" },
    { id: "t7", time: "20:00", task: "Dinner", activity: "Dinner", room: "Kitchen", durationMin: 45, repeat: "daily" },
    { id: "t8", time: "23:00", task: "Sleep", activity: "Sleeping", room: "Bedroom", durationMin: 480, repeat: "daily" },
  ];
}

const ROUTINE: { activity: ActivityLabel; room: Room; minute: number; dur: number }[] = [
  { activity: "Showering", room: "Bathroom", minute: 7 * 60, dur: 20 },
  { activity: "Breakfast", room: "Kitchen", minute: 8 * 60, dur: 30 },
  { activity: "Study", room: "Study", minute: 10 * 60, dur: 120 },
  { activity: "Lunch", room: "Kitchen", minute: 13 * 60, dur: 40 },
  { activity: "Study", room: "Study", minute: 15 * 60, dur: 90 },
  { activity: "Exercise", room: "Gym", minute: 18 * 60 + 13, dur: 45 },
  { activity: "Dinner", room: "Kitchen", minute: 20 * 60, dur: 45 },
  { activity: "Relaxing", room: "Living Room", minute: 21 * 60, dur: 90 },
  { activity: "Sleeping", room: "Bedroom", minute: 23 * 60, dur: 450 },
];

const startOfDay = (d: Date) => {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x.getTime();
};

export function seedHistory(now: number, days = 14): ActivityHistoryEntry[] {
  const rand = rng(20260926);
  const out: ActivityHistoryEntry[] = [];
  for (let d = days; d >= 0; d--) {
    const dayStart = startOfDay(new Date(now - d * 86400000));
    for (const r of ROUTINE) {
      const jitter = Math.round((rand() - 0.5) * 50);
      const start = dayStart + (r.minute + jitter) * 60000;
      if (start > now) continue;
      out.push({
        id: `h-${d}-${r.activity}-${r.minute}`,
        activity: r.activity,
        room: r.room,
        start,
        end: Math.min(now, start + r.dur * 60000),
      });
    }
  }
  return out.sort((a, b) => a.start - b.start);
}

export function seedAppliances(now: number): Appliance[] {
  return [
    { id: "a1", name: "Kitchen Lights", room: "Kitchen", on: true, watts: 45, since: now - 35 * 60000 },
    { id: "a2", name: "Living Room TV", room: "Living Room", on: false, watts: 120, since: now - 200 * 60000 },
    { id: "a3", name: "Air Conditioner", room: "Bedroom", on: true, watts: 950, since: now - 90 * 60000 },
    { id: "a4", name: "Study Desk Plug", room: "Study", on: true, watts: 85, since: now - 150 * 60000 },
    { id: "a5", name: "Water Heater", room: "Bathroom", on: false, watts: 1800, since: now - 400 * 60000 },
    { id: "a6", name: "Treadmill", room: "Gym", on: false, watts: 600, since: now - 900 * 60000 },
  ];
}

export function seedSensorEvents(now: number, room: Room): SensorEvent[] {
  const rand = rng(77771);
  const rooms: Room[] = ["Kitchen", "Living Room", "Study", "Bedroom", "Bathroom", room];
  const out: SensorEvent[] = [];
  for (let i = 24; i >= 0; i--) {
    const r = i < 5 ? room : rooms[Math.floor(rand() * rooms.length)]!;
    const types = ["motion", "light", "door", "temperature", "plug", "appliance"] as const;
    const t = types[Math.floor(rand() * types.length)]!;
    out.push({
      id: `s-${i}-${t}-${r}`,
      timestamp: now - i * 4 * 60000 - Math.floor(rand() * 60000),
      room: r,
      sensorType: t,
      sensorId: `${t.toUpperCase().slice(0, 4)}-${r.replace(/\s/g, "")}`,
      value:
        t === "temperature"
          ? 21 + rand() * 4
          : t === "plug"
            ? Math.round(rand() * 180)
            : rand() > 0.3
              ? 1
              : 0,
      unit: t === "temperature" ? "°C" : t === "plug" ? "W" : undefined,
      label: t === "appliance" ? `${r} appliance` : undefined,
    });
  }
  return out.sort((a, b) => a.timestamp - b.timestamp);
}

export function seedProfile(): Profile {
  return {
    name: "Alex Rivera",
    home: "Apartment 12B",
    wakeTime: "07:00",
    notifyAnomalies: true,
    notifyPlanDrift: true,
    storeLocally: true,
    mode: "demo",
  };
}

export function currentRoomFromHistory(history: ActivityHistoryEntry[], now: number): Room {
  const active = history.filter((h) => h.start <= now).slice(-1)[0];
  return active?.room ?? "Living Room";
}

export function energyByHour(appliances: Appliance[], now: number) {
  const rand = rng(4242);
  const hour = new Date(now).getHours();
  const base = appliances.reduce((a, b) => a + b.watts, 0) / 1000;
  return Array.from({ length: 24 }, (_, h) => ({
    hour: h,
    kwh:
      h > hour
        ? 0
        : Number(
            (base * (0.12 + (h >= 6 && h <= 9 ? 0.25 : 0) + (h >= 17 && h <= 22 ? 0.35 : 0)) * (0.7 + rand() * 0.6)).toFixed(2),
          ),
  }));
}
