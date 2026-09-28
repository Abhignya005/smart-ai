import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export const Route = createFileRoute("/explorer")({
  component: DatasetExplorer,
});

const sampleData = [
  { time: "06:00", power: 0.8, room: "Bedroom", motion: "ON" },
  { time: "07:30", power: 3.2, room: "Kitchen", motion: "ON" },
  { time: "09:00", power: 1.1, room: "Living", motion: "OFF" },
  { time: "12:00", power: 1.4, room: "Kitchen", motion: "ON" },
  { time: "18:00", power: 4.5, room: "Living", motion: "ON" },
];

const chartData = [
  { name: 'Mon', energy: 12 }, { name: 'Tue', energy: 15 }, { name: 'Wed', energy: 14 },
  { name: 'Thu', energy: 18 }, { name: 'Fri', energy: 16 }, { name: 'Sat', energy: 22 }, { name: 'Sun', energy: 24 }
];

function DatasetExplorer() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dataset Explorer</h1>
        <p className="text-muted-foreground mt-2">Inspect the uploaded schema and feature engineering results.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Feature Engineering Pipeline</CardTitle>
            <CardDescription>Generated features ready for ML</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">Hour</span>
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">Day of Week</span>
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">Weekend Indicator</span>
              <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">Rolling Energy (1h)</span>
              <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">Power Change Delta</span>
              <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Time Since Prev Event</span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Daily Energy Trends</CardTitle>
          </CardHeader>
          <CardContent className="h-[150px]">
             <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Bar dataKey="energy" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Data Preview (First 5 Rows)</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>Total Power (kW)</TableHead>
                <TableHead>Active Room</TableHead>
                <TableHead>Motion Sensor</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sampleData.map((row, i) => (
                <TableRow key={i}>
                  <TableCell>{row.time}</TableCell>
                  <TableCell>{row.power}</TableCell>
                  <TableCell>{row.room}</TableCell>
                  <TableCell>{row.motion}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
