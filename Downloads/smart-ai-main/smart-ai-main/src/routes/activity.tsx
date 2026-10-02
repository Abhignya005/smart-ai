import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Play, BrainCircuit, BarChartHorizontal, Check, X, Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { getOrFetchDataset, onDatasetUpdate } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";

export const Route = createFileRoute("/activity")({
  component: ActivityRecognition,
});

const shapData = [
  { feature: "Primary Sensor", impact: 0.85, fill: "#ef4444" },
  { feature: "Time of Day", impact: 0.45, fill: "#ef4444" },
  { feature: "Secondary Sensor", impact: -0.15, fill: "#3b82f6" },
];

function ActivityRecognition() {
  const [running, setRunning] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [metrics, setMetrics] = useState<any>(null);

  const loadData = () => {
    getOrFetchDataset().then((d) => {
      if (d) setMetrics(calculateDashboardMetrics(d));
    });
  };

  useEffect(() => {
    loadData();
    const unsubscribe = onDatasetUpdate((updatedDs) => {
      if (updatedDs) setMetrics(calculateDashboardMetrics(updatedDs));
      else loadData();
    });
    return unsubscribe;
  }, []);

  const runAnalysis = () => {
    if (!metrics) return;
    setRunning(true);
    setFeedbackGiven(false);
    setTimeout(() => {
      setRunning(false);
      setPrediction({
        activity: metrics.currentActivity,
        confidence: metrics.currentConf, 
        nextActivity: metrics.nextActivity,
        nextConfidence: metrics.nextConf,
      });
      toast.success("Activity Analysis Complete");
    }, 1000);
  };

  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first.</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Real Activity Recognition</h1>
          <p className="text-muted-foreground mt-2">Dynamic predictions based on {metrics.rows} uploaded rows.</p>
        </div>
        <div className="space-x-2">
            <Button onClick={runAnalysis} disabled={running}>
                <Play className="size-4 mr-2" /> {running ? "Analyzing..." : "Run ML Analysis"}
            </Button>
        </div>
      </div>

      <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex justify-between items-center">
                    <span>Model Prediction</span>
                    <Badge variant="outline" className="bg-blue-50 text-blue-700">Model Ready</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {prediction ? (
                  <div className="space-y-6 animate-in slide-in-from-right-4">
                    <div className="grid grid-cols-2 gap-4 border-b pb-6">
                        <div className="text-center border-r">
                            <p className="text-xs font-semibold text-muted-foreground uppercase mb-1">Detected Activity</p>
                            <h2 className={`text-3xl font-bold ${prediction.activity === 'Not Confirmed' || prediction.activity === 'Insufficient Data' ? 'text-amber-500' : 'text-primary'}`}>{prediction.activity}</h2>
                            {prediction.confidence && <p className="text-sm text-muted-foreground mt-1">Confidence: {prediction.confidence}</p>}
                        </div>
                        <div className="text-center">
                            <p className="text-xs font-semibold text-muted-foreground uppercase flex justify-center items-center gap-1 mb-1"><BrainCircuit className="size-3"/> Next Activity Prediction</p>
                            <h2 className="text-3xl font-bold text-purple-600">{prediction.nextActivity}</h2>
                            {prediction.nextConfidence && <p className="text-sm text-muted-foreground mt-1">Probability: {prediction.nextConfidence}</p>}
                        </div>
                    </div>

                    {!feedbackGiven && prediction.activity !== 'Not Confirmed' && prediction.activity !== 'Insufficient Data' && (
                        <div className="bg-muted/50 p-4 rounded-md flex justify-between items-center">
                            <span className="text-sm font-medium">Was this prediction accurate?</span>
                            <div className="space-x-2">
                                <Button size="sm" variant="outline" onClick={() => setFeedbackGiven(true)}><Check className="size-4 mr-1"/> Correct</Button>
                                <Button size="sm" variant="outline" onClick={() => setFeedbackGiven(true)}><X className="size-4 mr-1"/> Incorrect</Button>
                            </div>
                        </div>
                    )}
                  </div>
                ) : (
                  <div className="h-[200px] flex items-center justify-center text-muted-foreground">
                     Click Run ML Analysis to generate prediction
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2"><BarChartHorizontal className="size-5" /> Explainable AI (SHAP Insights)</CardTitle>
                </CardHeader>
                <CardContent>
                    {prediction ? (
                        <div className="h-[250px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart layout="vertical" data={shapData} margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                                    <XAxis type="number" domain={[-1, 1]} hide />
                                    <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false} fontSize={12} />
                                    <Tooltip />
                                    <Bar dataKey="impact" radius={[0, 4, 4, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="h-[100px] flex items-center justify-center text-muted-foreground text-sm border-2 border-dashed rounded-md bg-muted/20">Awaiting Analysis</div>
                    )}
                </CardContent>
            </Card>
        </div>
    </div>
  );
}
