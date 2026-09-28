import { createFileRoute } from "@tanstack/react-router";
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
