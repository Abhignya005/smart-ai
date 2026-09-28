import { createFileRoute } from "@tanstack/react-router";
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
