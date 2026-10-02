// Explainable demo inference engine.
//
// This module is intentionally shaped like a model provider: every exported
// function takes plain feature inputs and returns scored outputs with
// reasons. A Python FastAPI service (Random Forest / XGBoost for activity and
// next-activity, Isolation Forest for anomalies) can implement the same
// interface and be swapped in without touching the UI.

import type {
  ActivityHistoryEntry,
  ActivityLabel,
  ActivityPrediction,
  ActivityScore,
  AnomalyEvent,
  Appliance,
  PlanComparison,
  RoutineBaseline,
  Room,
  ScheduleTask,
  SensorEvent,
} from "./types";
import { ACTIVITIES } from "./types";

export interface ActivityFeatures {
  minuteOfDay: number;
  dayOfWeek: number;
  room: Room;
  recentEvents: SensorEvent[];
  previousActivity?: ActivityLabel;
}

export interface InferenceProvider {
  recognizeActivity(f: ActivityFeatures): ActivityPrediction;
  predictNext(
    f: ActivityFeatures,
    history: ActivityHistoryEntry[],
    baselines: RoutineBaseline[],
  ): ActivityScore;
}

export const minuteOfDay = (ts: number) => {
  const d = new Date(ts);
  return d.getHours() * 60 + d.getMinutes();
};

export const formatMinute = (m: number) => {
  const mm = ((Math.round(m) % 1440) + 1440) % 1440;
  const h = Math.floor(mm / 60);
  const min = mm % 60;
  const suffix = h >= 12 ? "PM" : "AM";
  const h12 = h % 12 === 0 ? 12 : h % 12;
  return `${h12}:${String(min).padStart(2, "0")} ${suffix}`;
};

/** Typical time windows (minutes of day) used as a prior. */
const TIME_PRIOR: Record<ActivityLabel, [number, number]> = {
  Sleeping: [1380, 420],
  Breakfast: [450, 540],
  Cooking: [1080, 1170],
  Study: [600, 780],
  Lunch: [780, 840],
  Exercise: [1050, 1140],
  Relaxing: [1200, 1320],
  Dinner: [1170, 1245],
  Showering: [420, 480],
  "Leaving Home": [540, 600],
  Away: [560, 1000],
};

const ROOM_PRIOR: Record<ActivityLabel, Room[]> = {
  Sleeping: ["Bedroom"],
  Breakfast: ["Kitchen"],
  Cooking: ["Kitchen"],
  Study: ["Study"],
  Lunch: ["Kitchen"],
  Exercise: ["Gym", "Living Room"],
  Relaxing: ["Living Room"],
  Dinner: ["Kitchen", "Living Room"],
  Showering: ["Bathroom"],
  "Leaving Home": ["Entrance"],
  Away: ["Away"],
};

const inWindow = (m: number, [a, b]: [number, number]) =>
  a <= b ? m >= a && m <= b : m >= a || m <= b;

const softmax = (scores: number[], temp = 1.4) => {
  const max = Math.max(...scores);
  const exps = scores.map((s) => Math.exp((s - max) / temp));
  const sum = exps.reduce((a, b) => a + b, 0) || 1;
  return exps.map((e) => e / sum);
};

export function recognizeActivity(f: ActivityFeatures): ActivityPrediction {
  const recent = f.recentEvents.slice(-14);
  const reasonsFor: Record<string, string[]> = {};
  const raw = ACTIVITIES.map((activity) => {
    let score = 0;
    const reasons: string[] = [];

    if (inWindow(f.minuteOfDay, TIME_PRIOR[activity])) {
      score += 2.2;
      reasons.push(`Time of day matches the usual ${activity.toLowerCase()} window`);
    }
    if (ROOM_PRIOR[activity].includes(f.room)) {
      score += 2.6;
      reasons.push(`Current room is ${f.room}`);
    }

    for (const ev of recent) {
      const roomMatch = ROOM_PRIOR[activity].includes(ev.room);
      if (!roomMatch) continue;
      if (ev.sensorType === "motion" && ev.value > 0) {
        score += 0.8;
        reasons.push(`Motion detected in ${ev.room}`);
      }
      if (ev.sensorType === "light" && ev.value > 0) {
        score += 0.4;
        reasons.push(`Lights on in ${ev.room}`);
      }
      if (ev.sensorType === "appliance" && ev.value > 0) {
        score += 1.0;
        reasons.push(`${ev.label ?? "Appliance"} is ON`);
      }
      if (ev.sensorType === "plug" && ev.value > 40) {
        score += 0.9;
        reasons.push(`Smart plug draw ${Math.round(ev.value)}W in ${ev.room}`);
      }
      if (ev.sensorType === "door" && ev.value > 0) {
        score += 0.5;
        reasons.push(`Door event in ${ev.room}`);
      }
      if (ev.sensorType === "temperature" && activity === "Showering" && ev.value > 24) {
        score += 1.1;
        reasons.push(`Bathroom temperature rise (${ev.value.toFixed(1)}°C)`);
      }
    }

    if (f.previousActivity === activity) {
      score += 0.6;
      reasons.push("Continuation of the previous detected activity");
    }
    if (activity === "Sleeping" && recent.filter((e) => e.value > 0).length < 2) {
      score += 1.0;
      reasons.push("Very little sensor activity");
    }

    reasonsFor[activity] = Array.from(new Set(reasons)).slice(0, 4);
    return score;
  });

  const probs = softmax(raw);
  const scored: ActivityScore[] = ACTIVITIES.map((activity, i) => ({
    activity,
    probability: probs[i] ?? 0,
    reasons: reasonsFor[activity] ?? [],
  })).sort((a, b) => b.probability - a.probability);

  const top = scored[0]!;
  return {
    timestamp: Date.now(),
    top,
    alternatives: scored.slice(1, 5),
    room: f.room,
    evidence: recent
      .filter((e) => ROOM_PRIOR[top.activity].includes(e.room))
      .slice(-6),
    source: "demo-inference",
  };
}

const TRANSITIONS: Partial<Record<ActivityLabel, ActivityLabel[]>> = {
  Sleeping: ["Showering", "Breakfast"],
  Showering: ["Breakfast", "Study"],
  Breakfast: ["Study", "Leaving Home"],
  Study: ["Lunch", "Relaxing"],
  Lunch: ["Study", "Relaxing"],
  Relaxing: ["Dinner", "Exercise"],
  Exercise: ["Showering", "Dinner"],
  Cooking: ["Dinner"],
  Dinner: ["Relaxing", "Sleeping"],
  "Leaving Home": ["Away"],
  Away: ["Relaxing", "Dinner"],
};

export function predictNext(
  f: ActivityFeatures,
  history: ActivityHistoryEntry[],
  baselines: RoutineBaseline[],
): ActivityScore {
  const current = f.previousActivity;
  const counts = new Map<ActivityLabel, number>();

  // Historical transition frequency
  for (let i = 1; i < history.length; i++) {
    if (history[i - 1]!.activity === current) {
      const nxt = history[i]!.activity;
      counts.set(nxt, (counts.get(nxt) ?? 0) + 1.4);
    }
  }
  // Prior transitions
  for (const a of TRANSITIONS[current ?? "Relaxing"] ?? []) {
    counts.set(a, (counts.get(a) ?? 0) + 1.2);
  }
  // Upcoming routine baselines
  for (const b of baselines) {
    const delta = b.typicalMinuteOfDay - f.minuteOfDay;
    if (delta > 0 && delta < 150) {
      counts.set(b.activity, (counts.get(b.activity) ?? 0) + 2.2 - delta / 100);
    }
  }
  if (counts.size === 0) counts.set("Relaxing", 1);

  const entries = [...counts.entries()].filter(([a]) => a !== current);
  const pool = entries.length ? entries : [...counts.entries()];
  const probs = softmax(pool.map(([, v]) => v));
  const ranked = pool
    .map(([activity], i) => ({ activity, probability: probs[i] ?? 0 }))
    .sort((a, b) => b.probability - a.probability);

  const best = ranked[0]!;
  const baseline = baselines.find((b) => b.activity === best.activity);
  const reasons = [
    current ? `Usually follows ${current}` : "Based on time of day",
    `Day of week pattern (${["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][f.dayOfWeek]})`,
    baseline
      ? `Typical ${best.activity.toLowerCase()} time is around ${formatMinute(baseline.typicalMinuteOfDay)}`
      : "No strong historical baseline yet",
    `Current room: ${f.room}`,
  ];
  return { activity: best.activity, probability: best.probability, reasons };
}

export function learnBaselines(
  history: ActivityHistoryEntry[],
  tasks: ScheduleTask[],
): RoutineBaseline[] {
  const byActivity = new Map<ActivityLabel, number[]>();
  for (const h of history) {
    const arr = byActivity.get(h.activity) ?? [];
    arr.push(minuteOfDay(h.start));
    byActivity.set(h.activity, arr);
  }
  const out: RoutineBaseline[] = [];
  for (const [activity, mins] of byActivity) {
    if (mins.length < 2) continue;
    const mean = mins.reduce((a, b) => a + b, 0) / mins.length;
    const spread = Math.sqrt(
      mins.reduce((a, b) => a + (b - mean) ** 2, 0) / mins.length,
    );
    const planned = tasks.find((t) => t.activity === activity);
    let adherence = 0.7;
    if (planned) {
      const [ph, pm] = planned.time.split(":").map(Number);
      const plannedMin = (ph ?? 0) * 60 + (pm ?? 0);
      const hits = mins.filter((m) => Math.abs(m - plannedMin) <= 30).length;
      adherence = hits / mins.length;
    }
    out.push({
      activity,
      typicalMinuteOfDay: mean,
      spreadMin: Math.round(spread),
      samples: mins.length,
      adherence,
    });
  }
  return out.sort((a, b) => a.typicalMinuteOfDay - b.typicalMinuteOfDay);
}

export function comparePlan(
  tasks: ScheduleTask[],
  todayHistory: ActivityHistoryEntry[],
  now: number,
  currentActivity?: ActivityLabel,
): PlanComparison[] {
  const nowMin = minuteOfDay(now);
  return tasks
    .slice()
    .sort((a, b) => a.time.localeCompare(b.time))
    .map((task) => {
      const [h, m] = task.time.split(":").map(Number);
      const planned = (h ?? 0) * 60 + (m ?? 0);
      const matches = todayHistory.filter((e) => e.activity === task.activity);
      const onTime = matches.find(
        (e) => Math.abs(minuteOfDay(e.start) - planned) <= 20,
      );
      const late = matches.find((e) => {
        const d = minuteOfDay(e.start) - planned;
        return d > 20 && d <= 75;
      });
      const anyMatch = matches[0];

      if (planned > nowMin + 5 && !anyMatch) {
        return {
          task,
          status: "UPCOMING" as const,
          explanation: `Scheduled for ${task.time} in the ${task.room}.`,
          evidenceStrength: 0,
        };
      }
      if (onTime) {
        return {
          task,
          status: "COMPLETED" as const,
          explanation: `Detected in ${onTime.room} at ${formatMinute(minuteOfDay(onTime.start))}, within the planned window.`,
          detectedAt: onTime.start,
          evidenceStrength: 0.9,
        };
      }
      if (late) {
        const diff = Math.round(minuteOfDay(late.start) - planned);
        return {
          task,
          status: "DELAYED" as const,
          explanation: `Detected ${diff} min after the planned time, in the ${late.room}.`,
          detectedAt: late.start,
          evidenceStrength: 0.75,
        };
      }
      if (currentActivity && currentActivity !== task.activity && nowMin - planned < 45 && nowMin >= planned) {
        return {
          task,
          status: "TEMPORARY DEVIATION" as const,
          explanation: `Currently detected as ${currentActivity}. The planned activity may still happen shortly.`,
          evidenceStrength: 0.45,
        };
      }
      if (anyMatch) {
        return {
          task,
          status: "DEVIATED" as const,
          explanation: `Happened at ${formatMinute(minuteOfDay(anyMatch.start))}, well outside the planned window.`,
          detectedAt: anyMatch.start,
          evidenceStrength: 0.6,
        };
      }
      if (nowMin - planned > 90) {
        return {
          task,
          status: "DEVIATED" as const,
          explanation: "No matching sensor evidence was recorded for this task today.",
          evidenceStrength: 0.3,
        };
      }
      return {
        task,
        status: "NOT CONFIRMED" as const,
        explanation: "Sensor evidence so far is not strong enough to confirm this task.",
        evidenceStrength: 0.2,
      };
    });
}

/** Isolation-Forest-style feature vector, scored with an explainable fallback. */
export function detectAnomaly(
  currentActivity: ActivityLabel,
  now: number,
  baselines: RoutineBaseline[],
  recent: SensorEvent[],
  appliances: Appliance[],
): AnomalyEvent | null {
  const reasons: string[] = [];
  let score = 0;
  const nowMin = minuteOfDay(now);

  const base = baselines.find((b) => b.activity === currentActivity);
  if (base) {
    const deviation = Math.abs(nowMin - base.typicalMinuteOfDay);
    const tolerance = Math.max(25, base.spreadMin * 2);
    if (deviation > tolerance) {
      score += Math.min(0.45, deviation / 400);
      reasons.push(
        `${currentActivity} is happening ${Math.round(deviation)} min from the usual ${formatMinute(base.typicalMinuteOfDay)}`,
      );
    }
  } else {
    score += 0.12;
    reasons.push(`Not much history yet for ${currentActivity}`);
  }

  const nightMotion = recent.filter(
    (e) => e.sensorType === "motion" && e.value > 0 && (minuteOfDay(e.timestamp) > 1410 || minuteOfDay(e.timestamp) < 300),
  );
  if (nightMotion.length >= 3) {
    score += 0.25;
    reasons.push(`${nightMotion.length} night-time motion events recorded`);
  }

  const leftOn = appliances.filter((a) => a.on && a.room !== "Away");
  if (currentActivity === "Away" || currentActivity === "Leaving Home") {
    if (leftOn.length) {
      score += 0.3;
      reasons.push(
        `${leftOn.map((a) => a.name).join(", ")} still running while nobody is home`,
      );
    }
  }

  const rooms = new Set(recent.slice(-10).map((e) => e.room));
  if (rooms.size >= 5) {
    score += 0.18;
    reasons.push(`Unusually frequent room transitions (${rooms.size} rooms recently)`);
  }

  if (!reasons.length) return null;
  score = Math.min(0.98, score);
  return {
    id: `an-${now}`,
    timestamp: now,
    score,
    severity: score > 0.6 ? "review" : score > 0.3 ? "notable" : "info",
    title:
      score > 0.6
        ? "Pattern worth reviewing"
        : score > 0.3
          ? "Notable change in routine"
          : "Minor routine variation",
    reasons,
  };
}

export function energyRecommendations(
  appliances: Appliance[],
  currentActivity: ActivityLabel,
  room: Room,
): string[] {
  const tips: string[] = [];
  const on = appliances.filter((a) => a.on);
  if ((currentActivity === "Away" || currentActivity === "Leaving Home") && on.length) {
    tips.push(
      `You appear to be heading out while ${on.map((a) => a.name).join(", ")} ${on.length > 1 ? "are" : "is"} still on.`,
    );
  }
  const idle = on.filter((a) => a.room !== room && a.room !== "Away" && a.watts > 40);
  for (const a of idle) {
    tips.push(`${a.name} is drawing ~${a.watts}W in the ${a.room}, where no one is currently detected.`);
  }
  if (currentActivity === "Sleeping") {
    const bright = on.filter((a) => a.name.toLowerCase().includes("light"));
    if (bright.length) tips.push("Lights are still on during your usual sleep window.");
  }
  if (!tips.length) tips.push("Appliance usage looks consistent with your current activity.");
  return tips;
}

export const demoProvider: InferenceProvider = { recognizeActivity, predictNext };
