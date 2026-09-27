import { createFileRoute } from "@tanstack/react-router";
import { useSmartHome } from "@/lib/smarthome/store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { clockTime } from "@/components/smarthome/ui-bits";

export const Route = createFileRoute("/routine")({
  component: RoutineLearning,
});

function RoutineLearning() {
  const { baselines, history } = useSmartHome();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Personal Routine Learning</h1>
        <p className="text-muted-foreground">Historical baseline generated from past behavior.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(baselines).map(([activity, data]) => (
          <Card key={activity}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{activity}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Typical Time:</span>
                  <span className="font-medium">{clockTime(data.typicalTime)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Avg Duration:</span>
                  <span className="font-medium">{Math.round(data.avgDurationMin)} min</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Frequency:</span>
                  <span className="font-medium">{data.count} times</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

