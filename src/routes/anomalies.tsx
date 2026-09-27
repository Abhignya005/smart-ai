import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/anomalies")({
  component: AnomaliesDetection,
});

function AnomaliesDetection() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/detect/anomaly')
      .then(res => res.json())
      .then(json => {
        if (json.success) setData(json.anomalies);
      })
      .catch(err => console.error(err));
  }, []);

  if (!data) return <div className="p-8">Loading ML Anomaly Detection...</div>;

  const current = data[data.length - 1];
  const detectedAnomalies = data.filter((d: any) => d.is_anomaly);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">ML Anomaly Detection</h1>
        <p className="text-muted-foreground mt-2">Unsupervised outlier detection using Isolation Forest</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Current Status</CardTitle>
            <CardDescription>Based on real-time Isolation Forest scoring</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-4xl font-bold text-primary">
                  {current.is_anomaly ? "Anomalous" : "Normal"}
                </span>
                <Badge variant={current.is_anomaly ? "destructive" : "default"} className="text-sm">
                  Score: {current.score.toFixed(3)}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mt-4">
                The Isolation Forest model considers this behavior {current.is_anomaly ? "highly unusual" : "expected"} compared to historical routines.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Anomalies Found</CardTitle>
            <CardDescription>Out of the last 50 samples</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-destructive mb-2">
              {detectedAnomalies.length}
            </div>
            <p className="text-sm text-muted-foreground">
              Anomalies are flagged when power consumption and motion patterns deviate significantly from the baseline.
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Anomaly Feed</CardTitle>
          <CardDescription>Historical flagged events</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {detectedAnomalies.length === 0 ? (
              <p className="text-sm text-muted-foreground">No recent anomalies detected in the sample window.</p>
            ) : (
              detectedAnomalies.slice().reverse().map((a: any, i: number) => (
                <div key={i} className="flex items-center justify-between p-3 border rounded-lg border-red-500/20 bg-red-500/5">
                  <div className="flex flex-col">
                    <span className="font-medium text-red-600">Unusual Activity Detected</span>
                    <span className="text-xs text-muted-foreground">{a.timestamp}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">{a.power.toFixed(1)}W Power, {a.motion_count} Motions</div>
                    <div className="text-xs text-muted-foreground">Activity: {a.actual_activity}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
