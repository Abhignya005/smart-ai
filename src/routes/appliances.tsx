import { createFileRoute } from "@tanstack/react-router";
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
