import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/activity")({
  component: ActivityRecognition,
});

function ActivityRecognition() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/predict/activity')
      .then(res => res.json())
      .then(json => {
        if (json.success) setData(json.predictions);
      })
      .catch(err => console.error(err));
  }, []);

  if (!data) return <div className="p-8">Loading ML Activity Predictions...</div>;

  const current = data[data.length - 1];
  const isCorrect = current.predicted === current.actual;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Activity Recognition</h1>
        <p className="text-muted-foreground mt-2">Live inference from Random Forest Classifier</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Current ML Prediction</CardTitle>
            <CardDescription>Based on the latest sensor window</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-4xl font-bold text-primary">{current.predicted}</span>
                <Badge variant={isCorrect ? "default" : "destructive"} className="text-sm">
                  {isCorrect ? "Correct Match" : "Misclassification"}
                </Badge>
              </div>
              <div className="flex justify-between text-sm text-muted-foreground mt-4">
                <span>Confidence: <span className="font-medium text-foreground">{current.confidence}%</span></span>
                <span>Ground Truth: <span className="font-medium text-foreground">{current.actual}</span></span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Sensor Features</CardTitle>
            <CardDescription>Inputs to the Random Forest model</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(current.features).map(([sensor, val]: any) => (
                <div key={sensor} className="flex justify-between text-sm border-b pb-2">
                  <span className="capitalize">{sensor.replace('_', ' ')}</span>
                  <span className="font-medium">{val > 0 ? (val === 1 ? "Active" : `${val.toFixed(1)}W`) : "Inactive / 0W"}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Prediction History</CardTitle>
          <CardDescription>Last 20 classification results</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.slice().reverse().map((pred: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex flex-col">
                  <span className="font-medium">{pred.predicted} <span className="text-xs text-muted-foreground ml-2">({pred.confidence}%)</span></span>
                  <span className="text-xs text-muted-foreground">{pred.timestamp}</span>
                </div>
                <Badge variant={pred.predicted === pred.actual ? "secondary" : "outline"}>
                  True: {pred.actual}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
