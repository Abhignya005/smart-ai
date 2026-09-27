import { createFileRoute } from "@tanstack/react-router";
import { useSmartHome } from "@/lib/smarthome/store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/energy")({
  component: EnergyDashboard,
});

function EnergyDashboard() {
  const { appliances, recommendations, toggleAppliance } = useSmartHome();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Energy & Appliances</h1>
        <p className="text-muted-foreground">Monitor smart plugs and appliance states.</p>
      </div>

      {recommendations.length > 0 && (
        <Card className="bg-primary/5 border-primary/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-primary">AI Recommendation</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside text-sm space-y-1">
              {recommendations.map((rec, i) => (
                <li key={i}>{rec}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {appliances.map(app => (
          <Card key={app.id}>
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
              <CardTitle className="text-base">{app.name}</CardTitle>
              <Badge variant={app.on ? "default" : "secondary"}>{app.on ? "ON" : "OFF"}</Badge>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-sm text-muted-foreground">{app.room}</div>
              <div className="text-2xl font-bold">{app.on ? app.watts : 0} <span className="text-sm font-normal text-muted-foreground">W</span></div>
              <Button size="sm" variant="outline" className="w-full mt-2" onClick={() => toggleAppliance(app.id)}>
                Toggle Power
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

