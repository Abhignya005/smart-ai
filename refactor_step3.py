import os
BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

pages = {
    "activity.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Activity, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { toast } from "sonner";

export const Route = createFileRoute("/activity")({
  component: ActivityRecognition,
});

function ActivityRecognition() {
  const [running, setRunning] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);

  const runAnalysis = () => {
    setRunning(true);
    setTimeout(() => {
      setRunning(false);
      setPrediction({
        activity: "Cooking",
        confidence: 91,
        alt: [{name: "Eating", conf: 5}, {name: "Cleaning", conf: 3}, {name: "Other", conf: 1}],
        evidence: { time: "18:00", room: "Kitchen", motion: "ON", power: "850W" }
      });
      toast.success("Activity Analysis Complete");
    }, 1500);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Activity Recognition</h1>
          <p className="text-muted-foreground mt-2">Infer human activities purely from anonymous ambient sensor data.</p>
        </div>
        <Button onClick={runAnalysis} disabled={running}>
            <Play className="size-4 mr-2" /> {running ? "Analyzing..." : "Run ML Analysis"}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Current State Vector</CardTitle>
            <CardDescription>Raw sensor input fed to the model</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
             <div className="flex justify-between border-b pb-2"><span>Time</span><span className="font-mono">18:00</span></div>
             <div className="flex justify-between border-b pb-2"><span>Room</span><span className="font-mono">Kitchen</span></div>
             <div className="flex justify-between border-b pb-2"><span>Motion</span><Badge>ON</Badge></div>
             <div className="flex justify-between border-b pb-2"><span>Light</span><Badge>ON</Badge></div>
             <div className="flex justify-between border-b pb-2"><span>Total Power</span><span className="font-mono">850W</span></div>
          </CardContent>
        </Card>

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
                <div className="text-center">
                    <h2 className="text-4xl font-bold text-primary">{prediction.activity}</h2>
                    <p className="text-sm text-muted-foreground mt-1">Confidence: {prediction.confidence}%</p>
                </div>
                <div className="space-y-2">
                    <p className="text-xs font-semibold text-muted-foreground uppercase">Alternative Predictions</p>
                    {prediction.alt.map((a:any) => (
                        <div key={a.name} className="flex items-center gap-4">
                            <span className="w-16 text-sm">{a.name}</span>
                            <Progress value={a.conf} className="h-2" />
                            <span className="text-xs text-muted-foreground">{a.conf}%</span>
                        </div>
                    ))}
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground py-12">
                 Click Run ML Analysis to generate prediction
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
""",
    "routine.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Clock, CalendarDays, CheckCircle2, AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/routine")({
  component: RoutineDiscovery,
});

function RoutineDiscovery() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Routine Pattern Discovery</h1>
        <p className="text-muted-foreground mt-2">Unsupervised machine learning discovers habits from historical temporal data.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Typical Wake-Up</CardTitle>
            <Clock className="size-4 text-muted-foreground absolute top-6 right-6" />
          </CardHeader>
          <CardContent><div className="text-2xl font-bold">7:12 AM</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Typical Work Departure</CardTitle>
            <Clock className="size-4 text-muted-foreground absolute top-6 right-6" />
          </CardHeader>
          <CardContent><div className="text-2xl font-bold">9:01 AM</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Typical Sleep</CardTitle>
            <Clock className="size-4 text-muted-foreground absolute top-6 right-6" />
          </CardHeader>
          <CardContent><div className="text-2xl font-bold">11:18 PM</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Analytical Feature: Planned vs Actual Routine</CardTitle>
          <CardDescription>Compare expected behavioral baselines against observed telemetry.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="border rounded-md p-4 bg-muted/20 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="space-y-1 text-center md:text-left">
                <p className="text-sm font-medium text-muted-foreground">Expected</p>
                <p className="font-bold">Exercise at 6:00 PM</p>
            </div>
            <div className="hidden md:block w-px h-10 bg-border"></div>
            <div className="space-y-1 text-center md:text-left">
                <p className="text-sm font-medium text-muted-foreground">Observed</p>
                <p className="font-bold">Watching TV (6:00 PM) → Exercise (6:23 PM)</p>
            </div>
            <div className="hidden md:block w-px h-10 bg-border"></div>
            <div className="text-center md:text-right">
                <Badge variant="outline" className="text-amber-600 bg-amber-50">DELAYED</Badge>
            </div>
          </div>

          <div className="border rounded-md p-4 bg-muted/20 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="space-y-1 text-center md:text-left">
                <p className="text-sm font-medium text-muted-foreground">Expected</p>
                <p className="font-bold">Sleep at 11:00 PM</p>
            </div>
            <div className="hidden md:block w-px h-10 bg-border"></div>
            <div className="space-y-1 text-center md:text-left">
                <p className="text-sm font-medium text-muted-foreground">Observed</p>
                <p className="font-bold">Living Room Activity until 1:00 AM</p>
            </div>
            <div className="hidden md:block w-px h-10 bg-border"></div>
            <div className="text-center md:text-right">
                <Badge variant="destructive">ROUTINE DEVIATION</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
""",
    "anomalies.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ShieldAlert, AlertCircle, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/anomalies")({
  component: AnomalyDetection,
});

function AnomalyDetection() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Anomaly & Safety Detection</h1>
          <p className="text-muted-foreground mt-2">Isolation Forest implementation to flag statistically significant deviations.</p>
        </div>
        <Badge variant="outline" className="bg-blue-50 text-blue-700 py-1">Model Ready</Badge>
      </div>

      <Card className="border-orange-200 shadow-sm">
        <CardHeader className="bg-orange-50/50 pb-4">
          <CardTitle className="flex items-center gap-2 text-orange-700">
             <AlertCircle className="size-5" /> Unusual activity detected. Review the event.
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4 space-y-4">
           <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
               <div className="space-y-3">
                   <div>
                       <p className="text-xs text-muted-foreground font-semibold uppercase">Timestamp</p>
                       <p className="font-medium">Today, 3:12 AM</p>
                   </div>
                   <div>
                       <p className="text-xs text-muted-foreground font-semibold uppercase">Sensor Evidence</p>
                       <p className="font-medium">Oven Active (Power Spiked to 2.4 kW)</p>
                   </div>
               </div>
               <div className="space-y-3">
                   <div>
                       <p className="text-xs text-muted-foreground font-semibold uppercase">Expected Behavior</p>
                       <p className="font-medium text-green-700">Oven usage between 6 PM–9 PM (Cooking Routine)</p>
                   </div>
                   <div>
                       <p className="text-xs text-muted-foreground font-semibold uppercase">Observed Behavior</p>
                       <p className="font-medium text-red-600">Oven active at 3:12 AM</p>
                   </div>
               </div>
           </div>
           
           <div className="bg-muted p-4 rounded-md flex justify-between items-center mt-4">
               <div>
                   <p className="font-bold">Anomaly Score: -0.84</p>
                   <p className="text-sm text-muted-foreground">High deviation from clustered behavioral norms.</p>
               </div>
               <div className="space-x-2">
                   <Button variant="outline" size="sm">Dismiss</Button>
                   <Button size="sm" variant="destructive">Flag for Review</Button>
               </div>
           </div>
        </CardContent>
      </Card>
      
      <h3 className="text-lg font-semibold mt-8 mb-2">Historical Log</h3>
      <div className="border rounded-md divide-y">
         <div className="p-4 flex justify-between items-center">
            <div className="flex gap-4 items-center">
                <CheckCircle2 className="text-green-500 size-5" />
                <div><p className="font-medium text-sm">Routine Normalcy</p><p className="text-xs text-muted-foreground">Yesterday, 11:00 PM</p></div>
            </div>
            <Badge variant="outline">Score: 0.92</Badge>
         </div>
      </div>
    </div>
  );
}
"""
}

for filename, content in pages.items():
    with open(os.path.join(ROUTES_DIR, filename), "w") as f:
        f.write(content)
print("Step 3 completed.")

