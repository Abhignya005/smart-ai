import os
BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

pages = {
    "energy.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Zap } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export const Route = createFileRoute("/energy")({
  component: EnergyIntelligence,
});

const chartData = [
  { time: '00:00', kw: 0.8 }, { time: '04:00', kw: 0.5 }, { time: '08:00', kw: 2.1 },
  { time: '12:00', kw: 1.4 }, { time: '16:00', kw: 1.8 }, { time: '20:00', kw: 4.8 }, { time: '23:59', kw: 1.2 }
];

function EnergyIntelligence() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Energy Intelligence</h1>
        <p className="text-muted-foreground mt-2">Macro-level analysis of household consumption trends.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Total Energy</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">482 kWh</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Average Consumption</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">2.1 kW</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Peak Consumption</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold text-red-500">4.8 kW</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Daily Average</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">16 kWh/day</div></CardContent></Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Energy vs Time</CardTitle>
          <CardDescription>Daily load profile highlighting the evening peak</CardDescription>
        </CardHeader>
        <CardContent className="h-[300px]">
           <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <XAxis dataKey="time" />
                <Tooltip />
                <Area type="monotone" dataKey="kw" stroke="#3b82f6" fill="#bfdbfe" />
              </AreaChart>
            </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
""",
    "forecast.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/forecast")({
  component: EnergyForecasting,
});

const data = [
  { time: '18:00', actual: 2.1, predicted: null },
  { time: '18:15', actual: 2.3, predicted: null },
  { time: '18:30', actual: 2.4, predicted: null },
  { time: '18:45', actual: null, predicted: 2.7 },
  { time: '19:00', actual: null, predicted: 3.1 },
];

function EnergyForecasting() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Energy Forecasting</h1>
          <p className="text-muted-foreground mt-2">Historical patterns estimate upcoming consumption via XGBoost.</p>
        </div>
        <Badge variant="outline" className="bg-blue-50 text-blue-700 py-1">Model Ready</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <Card>
            <CardHeader><CardTitle className="text-sm">Current Consumption</CardTitle></CardHeader>
            <CardContent><div className="text-3xl font-bold">2.4 kW</div></CardContent>
         </Card>
         <Card>
            <CardHeader><CardTitle className="text-sm">Predicted (+15 min)</CardTitle></CardHeader>
            <CardContent><div className="text-3xl font-bold text-blue-600">2.7 kW</div></CardContent>
         </Card>
         <Card>
            <CardHeader><CardTitle className="text-sm">Predicted (+30 min)</CardTitle></CardHeader>
            <CardContent><div className="text-3xl font-bold text-blue-600">3.1 kW</div></CardContent>
         </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Load Forecast Chart</CardTitle>
          <CardDescription>Actual vs Predicted Consumption</CardDescription>
        </CardHeader>
        <CardContent className="h-[300px]">
           <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <XAxis dataKey="time" />
                <Tooltip />
                <ReferenceLine x="18:30" stroke="red" strokeDasharray="3 3" label="Now" />
                <Line type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={3} name="Actual (kW)" />
                <Line type="monotone" dataKey="predicted" stroke="#3b82f6" strokeWidth={3} strokeDasharray="5 5" name="Predicted (kW)" />
              </LineChart>
            </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
""",
    "appliances.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/appliances")({
  component: ApplianceIntelligence,
});

const appliances = [
  { name: "AC", room: "Bedroom", state: "ON", power: "1.2 kW", daily: "8.5 kWh", freq: "High", time: "10 PM - 6 AM" },
  { name: "TV", room: "Living Room", state: "ON", power: "0.13 kW", daily: "0.6 kWh", freq: "Medium", time: "7 PM - 11 PM" },
  { name: "Refrigerator", room: "Kitchen", state: "ON", power: "0.15 kW", daily: "1.2 kWh", freq: "Always", time: "24/7" },
  { name: "Oven", room: "Kitchen", state: "OFF", power: "0 kW", daily: "2.1 kWh", freq: "Low", time: "6 PM - 7 PM" },
];

function ApplianceIntelligence() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Appliance Intelligence</h1>
        <p className="text-muted-foreground mt-2">Disaggregated appliance-level analytics.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Active Appliances Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Appliance</TableHead>
                <TableHead>Room</TableHead>
                <TableHead>Current State</TableHead>
                <TableHead>Power</TableHead>
                <TableHead>Daily Usage</TableHead>
                <TableHead>Typical Usage Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {appliances.map((a) => (
                <TableRow key={a.name}>
                  <TableCell className="font-medium">{a.name}</TableCell>
                  <TableCell>{a.room}</TableCell>
                  <TableCell><Badge variant={a.state === 'ON' ? 'default' : 'secondary'}>{a.state}</Badge></TableCell>
                  <TableCell>{a.power}</TableCell>
                  <TableCell>{a.daily}</TableCell>
                  <TableCell>{a.time}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
""",
    "models.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/models")({
  component: ModelCenter,
});

const models = [
  { name: "Activity Recognition", type: "Random Forest / XGBoost", purpose: "Infer human activities from sensor vectors.", input: "Motion, Light, Door, Room, Energy, Timestamp", output: "Predicted Activity + Confidence", status: "Model Ready" },
  { name: "Routine Learning", type: "Statistical Temporal Analysis / K-Means", purpose: "Discover recurring behavioral patterns.", input: "Time Series Energy, Event Logs", output: "Clustered Routine Profiles", status: "Model Ready" },
  { name: "Anomaly Detection", type: "Isolation Forest", purpose: "Flag unusual behavior for safety/security.", input: "Time, Total Power, Event Frequencies", output: "Anomaly Score (-1 or 1)", status: "Model Ready" },
  { name: "Energy Forecasting", type: "XGBoost", purpose: "Predict future energy demand.", input: "Historical Power, Temporal Features, Lags", output: "Predicted kW (Continuous)", status: "Model Ready" },
  { name: "Baseline Comparison", type: "Logistic Regression", purpose: "Establish baseline metrics for accuracy comparison.", input: "Standard Scaled Features", output: "Categorical Prediction", status: "Demo Analysis" }
];

function ModelCenter() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Model Center</h1>
        <p className="text-muted-foreground mt-2">Technical overview of the Machine Learning architectures deployed in this platform.</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {models.map((m) => (
          <Card key={m.name}>
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                  <CardTitle>{m.name}</CardTitle>
                  <Badge variant="outline" className={m.status === 'Model Ready' ? 'bg-blue-50 text-blue-700' : 'bg-gray-100'}>{m.status}</Badge>
              </div>
              <CardDescription className="font-mono text-xs mt-1">{m.type}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm mb-4">{m.purpose}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm bg-muted/30 p-3 rounded-md">
                 <div><span className="font-semibold block text-xs uppercase text-muted-foreground">Input Features</span> {m.input}</div>
                 <div><span className="font-semibold block text-xs uppercase text-muted-foreground">Output</span> {m.output}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
"""
}

for filename, content in pages.items():
    with open(os.path.join(ROUTES_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)
print("Step 4 completed.")

