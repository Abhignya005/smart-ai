// Core domain models for SmartHome AI.
// These mirror the tables a future backend would expose
// (users, schedule_tasks, sensor_events, activity_predictions,
// activity_history, routine_baselines, anomaly_events, appliances,
// energy_readings) so the repository layer can be swapped for real APIs.

export type Room =
  | "Bedroom"
  | "Kitchen"
  | "Living Room"
  | "Study"
  | "Bathroom"
  | "Gym"
  | "Entrance"
  | "Away";

export const ROOMS: Room[] = [
  "Bedroom",
  "Kitchen",
  "Living Room",
  "Study",
  "Bathroom",
  "Gym",
  "Entrance",
  "Away",
];

export type ActivityLabel =
  | "Sleeping"
  | "Breakfast"
  | "Cooking"
  | "Study"
  | "Lunch"
  | "Exercise"
  | "Relaxing"
  | "Dinner"
  | "Showering"
  | "Leaving Home"
  | "Away";

export const ACTIVITIES: ActivityLabel[] = [
  "Sleeping",
  "Breakfast",
  "Cooking",
  "Study",
  "Lunch",
  "Exercise",
  "Relaxing",
  "Dinner",
  "Showering",
  "Leaving Home",
  "Away",
];

export type SensorType =
  | "motion"
  | "door"
  | "light"
  | "temperature"
  | "appliance"
  | "plug";

export interface SensorEvent {
  id: string;
  timestamp: number;
  room: Room;
  sensorType: SensorType;
  /** Human readable sensor name, e.g. "PIR-Kitchen" */
  sensorId: string;
  /** Normalised value: boolean-ish sensors use 0/1, others use raw value */
  value: number;
  unit?: string;
  label?: string;
}

export interface ScheduleTask {
  id: string;
  time: string; // "HH:mm"
  task: string;
  activity: ActivityLabel;
  room: Room;
  durationMin: number;
  repeat: "daily" | "weekdays" | "weekends" | "once";
}

export type PlanStatus =
  | "COMPLETED"
  | "DELAYED"
  | "TEMPORARY DEVIATION"
  | "DEVIATED"
  | "NOT CONFIRMED"
  | "UPCOMING";

export interface PlanComparison {
  task: ScheduleTask;
  status: PlanStatus;
  explanation: string;
  detectedAt?: number;
  evidenceStrength: number; // 0..1
}

export interface ActivityScore {
  activity: ActivityLabel;
  probability: number; // 0..1
  reasons: string[];
}

export interface ActivityPrediction {
  timestamp: number;
  top: ActivityScore;
  alternatives: ActivityScore[];
  room: Room;
  evidence: SensorEvent[];
  source: "demo-inference";
}

export interface ActivityHistoryEntry {
  id: string;
  activity: ActivityLabel;
  room: Room;
  start: number;
  end: number;
}

export interface RoutineBaseline {
  activity: ActivityLabel;
  typicalMinuteOfDay: number;
  spreadMin: number;
  samples: number;
  adherence: number; // 0..1
}

export interface AnomalyEvent {
  id: string;
  timestamp: number;
  score: number; // 0..1
  severity: "info" | "notable" | "review";
  title: string;
  reasons: string[];
}

export interface Appliance {
  id: string;
  name: string;
  room: Room;
  on: boolean;
  watts: number;
  since: number;
}

export interface EnergyReading {
  hour: number; // 0..23
  kwh: number;
}

export interface Profile {
  name: string;
  home: string;
  wakeTime: string;
  notifyAnomalies: boolean;
  notifyPlanDrift: boolean;
  storeLocally: boolean;
  mode: "demo" | "live";
}
