# Smart Routine AI

Build a complete full-stack web app named “SmartHome AI — Personalized Routine & Activity Intelligence System” based on the PRD below. Prioritize a polished, responsive MVP that works well on a phone and desktop. Use TypeScript, Tailwind, shadcn/ui, and a clean modern smart-home/AI dashboard design. Do not merely create mock screens: implement the core interactions and data flow with realistic seeded/demo sensor data and a clear path to connect real sensors later.

CORE PRD REQUIREMENTS:
1. Product goal: understand a user's activities, compare them against their personal schedule, learn their normal routine, identify meaningful deviations, and predict what they are likely to do next.
2. Daily Plan Creation: CRUD schedule tasks with time, task, expected room, duration, repeat option. Example tasks include Breakfast, Study, Lunch, Exercise, Dinner, Sleep.
3. Smart-home sensor input: PIR/motion, door, light, temperature, appliance ON/OFF, smart-plug energy, room/location, timestamp, recent sensor events and transitions. Provide a Sensor Monitor page with live-looking demo stream and ability to add/simulate sensor events.
4. Activity Recognition: current activity prediction with confidence and alternative probabilities. Candidate ML models in the PRD are Random Forest/XGBoost with Logistic Regression baseline. For the web MVP, implement a realistic deterministic/inference service in TypeScript using sensor feature rules/weighted scoring so the UI is functional without a Python ML server, and structure the code so a real XGBoost/Random Forest API can replace it later. Clearly label demo inference as simulated/model-ready rather than falsely claiming trained ML.
5. Planned vs Actual Activity: compare schedule with detected activity and classify COMPLETED, DELAYED, TEMPORARY DEVIATION, DEVIATED, or NOT CONFIRMED. Do not claim failure when evidence is insufficient. Show timeline and explanations.
6. Next Activity Prediction: use current activity, previous activities, time, day of week, historical routine, current room, recent sensor events. Show predicted next activity and probability. Include model-ready architecture for XGBoost/Random Forest and optional LSTM/GRU later.
7. Personal Routine Learning: learn typical actual activity times over history and show personalized baseline, e.g. typical exercise time around 6:13 PM. Include routine trends/history.
8. Anomaly/Routine Deviation Detection: learn normal behavior and flag unusual patterns. Use an Isolation Forest-style feature interface in the architecture, with an explainable heuristic fallback for demo mode. Show anomaly score and reasons.
9. Appliance Verification: combine room motion/light/appliance/smart-plug signals as evidence for activities and show evidence strength.
10. Energy Intelligence: combine detected activity with appliance usage, show energy usage, appliance state, estimated consumption, and contextual recommendations such as leaving home while AC/TV/lights are still on.
11. Privacy-preserving positioning: no camera/microphone required; emphasize ambient sensor data and local/controlled data.

APP PAGES:
- Dashboard: current activity card, confidence, current room, planned activity, plan-vs-actual status, next activity prediction, anomaly alert, appliance/energy snapshot, sensor stream, quick actions.
- Daily Plan: calendar/timeline with add/edit/delete/repeat tasks.
- Activity Intelligence: current activity, probability distribution, recent timeline, evidence sensors, planned-vs-actual comparison.
- Routine Learning: historical activity patterns, typical times, adherence/deviation trends, personalized baseline.
- Anomalies: anomaly score, detected unusual patterns, explanation, timestamps, severity without alarmist language.
- Energy & Appliances: appliance states, estimated energy, activity correlation, recommendations.
- Sensors: sensor dashboard and demo event simulator.
- Settings: profile, privacy, notification preferences, demo/live mode.

DATA MODEL:
Create sensible typed models/tables for users/profile, schedule_tasks, sensor_events, activity_predictions, activity_history, routine_baselines, anomaly_events, appliances, energy_readings. If database is available, use it; otherwise make the app work immediately with local/demo data and a clean repository/service layer.

UX/UI:
- Professional hackathon-ready UI.
- Responsive mobile-first design because the user may operate it from an Android phone.
- Left sidebar on desktop and compact mobile navigation.
- Cards, charts, timeline, status badges, confidence bars, room indicators, sensor chips.
- Accessible contrast, clear typography, loading/empty/error states.
- Avoid excessive gradients or clutter.
- Include a small “Demo Mode” indicator so simulated data is transparent.

IMPORTANT IMPLEMENTATION DETAILS:
- Seed realistic sensor/activity/schedule history so the dashboard looks alive on first load.
- Add a “Simulate Event” action that updates the sensor stream and recalculates current activity, planned-vs-actual status, next activity prediction, appliance evidence and anomaly explanation.
- Use explainable scoring: whenever the app predicts an activity or anomaly, show contributing sensor evidence.
- Add charts for routine timing, adherence, anomaly trend and energy usage.
- Keep ML provider interfaces modular so a future Python FastAPI/XGBoost/Random Forest/Isolation Forest backend can be plugged in without rewriting the UI.
- Do not invent actual model accuracy metrics. If no trained dataset/model is connected, label predictions as “Demo inference”.
- Include helpful sample data and polished empty states.

Create the project now and make the MVP fully runnable, polished, and presentation-ready.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/66bc195d-5291-4631-9417-a1e1502ddc88).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
