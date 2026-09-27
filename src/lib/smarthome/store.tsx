import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  comparePlan,
  detectAnomaly,
  energyRecommendations,
  learnBaselines,
  minuteOfDay,
  predictNext,
  recognizeActivity,
} from "./inference";
import {
  currentRoomFromHistory,
  energyByHour,
  seedAppliances,
  seedHistory,
  seedProfile,
  seedSensorEvents,
  seedTasks,
} from "./seed";
import type {
  ActivityHistoryEntry,
  AnomalyEvent,
  Appliance,
  Profile,
  Room,
  ScheduleTask,
  SensorEvent,
} from "./types";

interface RawState {
  tasks: ScheduleTask[];
  history: ActivityHistoryEntry[];
  events: SensorEvent[];
  appliances: Appliance[];
  anomalies: AnomalyEvent[];
  profile: Profile;
  room: Room;
}

const STORAGE_KEY = "smarthome-ai-state-v1";

function buildInitial(): RawState {
  const now = Date.now();
  const history = seedHistory(now);
  const room = currentRoomFromHistory(history, now);
  return {
    tasks: seedTasks(),
    history,
    events: seedSensorEvents(now, room),
    appliances: seedAppliances(now),
    anomalies: [],
    profile: seedProfile(),
    room,
  };
}

interface StoreValue extends RawState {
  ready: boolean;
  prediction: ReturnType<typeof recognizeActivity>;
  next: ReturnType<typeof predictNext>;
  baselines: ReturnType<typeof learnBaselines>;
  plan: ReturnType<typeof comparePlan>;
  anomaly: AnomalyEvent | null;
  recommendations: string[];
  energy: { hour: number; kwh: number }[];
  addEvent: (e: Omit<SensorEvent, "id" | "timestamp">) => void;
  simulateRandomEvent: () => void;
  toggleAppliance: (id: string) => void;
  upsertTask: (t: ScheduleTask) => void;
  deleteTask: (id: string) => void;
  updateProfile: (p: Partial<Profile>) => void;
  resetDemo: () => void;
}

const Ctx = createContext<StoreValue | null>(null);

export function SmartHomeProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<RawState | null>(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setState(JSON.parse(saved) as RawState);
        return;
      }
    } catch {
      /* ignore corrupt storage */
    }
    setState(buildInitial());
  }, []);

  useEffect(() => {
    if (!state) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      /* storage full or unavailable */
    }
  }, [state]);

  const s = state ?? null;

  const derived = useMemo(() => {
    const base = s ?? buildInitialEmpty();
    const now = Date.now();
    const todayStart = new Date(now).setHours(0, 0, 0, 0);
    const todayHistory = base.history.filter((h) => h.start >= todayStart);
    const previous = todayHistory.slice(-1)[0]?.activity;
    const features = {
      minuteOfDay: minuteOfDay(now),
      dayOfWeek: new Date(now).getDay(),
      room: base.room,
      recentEvents: base.events,
      previousActivity: previous,
    };
    const prediction = recognizeActivity(features);
    const baselines = learnBaselines(base.history, base.tasks);
    const next = predictNext(
      { ...features, previousActivity: prediction.top.activity },
      base.history,
      baselines,
    );
    const plan = comparePlan(base.tasks, todayHistory, now, prediction.top.activity);
    const anomaly = detectAnomaly(
      prediction.top.activity,
      now,
      baselines,
      base.events,
      base.appliances,
    );
    return {
      prediction,
      baselines,
      next,
      plan,
      anomaly,
      recommendations: energyRecommendations(
        base.appliances,
        prediction.top.activity,
        base.room,
      ),
      energy: energyByHour(base.appliances, now),
    };
  }, [s]);

  const update = useCallback((fn: (prev: RawState) => RawState) => {
    setState((prev) => (prev ? fn(prev) : prev));
  }, []);

  const addEvent: StoreValue["addEvent"] = useCallback(
    (e) => {
      const now = Date.now();
      update((prev) => {
        const event: SensorEvent = { ...e, id: `s-${now}-${Math.round(now % 9973)}`, timestamp: now };
        const events = [...prev.events, event].slice(-60);
        const appliances = prev.appliances.map((a) =>
          a.room === e.room && (e.sensorType === "appliance" || e.sensorType === "plug")
            ? { ...a, on: e.value > 0, since: now }
            : a,
        );
        return { ...prev, events, room: e.room, appliances };
      });
    },
    [update],
  );

  const simulateRandomEvent = useCallback(() => {
    const rooms: Room[] = ["Kitchen", "Living Room", "Study", "Bedroom", "Gym", "Bathroom", "Entrance"];
    const types = ["motion", "light", "door", "temperature", "plug", "appliance"] as const;
    const room = rooms[Math.floor(Math.random() * rooms.length)]!;
    const sensorType = types[Math.floor(Math.random() * types.length)]!;
    addEvent({
      room,
      sensorType,
      sensorId: `${sensorType.toUpperCase().slice(0, 4)}-${room.replace(/\s/g, "")}`,
      value:
        sensorType === "temperature"
          ? Number((20 + Math.random() * 6).toFixed(1))
          : sensorType === "plug"
            ? Math.round(Math.random() * 200)
            : Math.random() > 0.25
              ? 1
              : 0,
      unit: sensorType === "temperature" ? "°C" : sensorType === "plug" ? "W" : undefined,
    });
  }, [addEvent]);

  const value: StoreValue = {
    ...(s ?? buildInitialEmpty()),
    ready: !!s,
    ...derived,
    addEvent,
    simulateRandomEvent,
    toggleAppliance: (id) =>
      update((prev) => ({
        ...prev,
        appliances: prev.appliances.map((a) =>
          a.id === id ? { ...a, on: !a.on, since: Date.now() } : a,
        ),
      })),
    upsertTask: (t) =>
      update((prev) => ({
        ...prev,
        tasks: prev.tasks.some((x) => x.id === t.id)
          ? prev.tasks.map((x) => (x.id === t.id ? t : x))
          : [...prev.tasks, t],
      })),
    deleteTask: (id) =>
      update((prev) => ({ ...prev, tasks: prev.tasks.filter((t) => t.id !== id) })),
    updateProfile: (p) => update((prev) => ({ ...prev, profile: { ...prev.profile, ...p } })),
    resetDemo: () => setState(buildInitial()),
  };

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

function buildInitialEmpty(): RawState {
  return {
    tasks: [],
    history: [],
    events: [],
    appliances: [],
    anomalies: [],
    profile: seedProfile(),
    room: "Living Room",
  };
}

export function useSmartHome() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useSmartHome must be used inside SmartHomeProvider");
  return ctx;
}
