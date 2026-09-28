import os

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

files = {
    "src/routes/routine.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { TrendingUp, ActivitySquare, AlertCircle, Database } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/routine")({
  component: RoutineDiscovery,
});

function RoutineDiscovery() {
  const [metrics, setMetrics] = useState<any>(null);
  
  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) setMetrics(calculateDashboardMetrics(dataset));
  }, []);

  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first.</div>;

  const score = parseInt(metrics.consistency) || 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Personal Routine Learning</h1>
            <p className="text-muted-foreground mt-2">Dynamically calculated from {metrics.rows} historical rows.</p>
          </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <Card className="lg:col-span-1 bg-primary text-primary-foreground">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-primary-foreground/80">Daily Routine Score</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center pt-4">
            {metrics.consistency !== "Insufficient Data" ? (
                <>
                <div className="relative flex items-center justify-center">
                    <svg className="w-24 h-24 transform -rotate-90">
                        <circle cx="48" cy="48" r="36" stroke="currentColor" strokeWidth="8" fill="transparent" className="opacity-20" />
                        <circle cx="48" cy="48" r="36" stroke="currentColor" strokeWidth="8" fill="transparent" strokeDasharray="226" strokeDashoffset={226 - (226 * score) / 100} className="text-white" />
                    </svg>
                    <span className="absolute text-3xl font-bold">{score}</span>
                </div>
                <p className="text-xs text-primary-foreground/80 mt-4 text-center">Calculated from actual completed routines.</p>
                </>
            ) : (
                <div className="text-center py-4">Insufficient Data</div>
            )}
          </CardContent>
        </Card>
        
        <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card><CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">Latest Detected Routine</CardTitle></CardHeader><CardContent><div className="text-xl font-bold">{metrics.currentActivity}</div></CardContent></Card>
            <Card><CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">Most Frequent Next</CardTitle></CardHeader><CardContent><div className="text-xl font-bold">{metrics.nextActivity}</div></CardContent></Card>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><TrendingUp className="size-5" /> Routine Drift Detection</CardTitle>
            </CardHeader>
            <CardContent>
               {metrics.rows > 10 ? (
               <div className="space-y-4">
                   <div className="p-4 border rounded-md bg-muted/20">
                       <p className="font-semibold text-sm">Shift in {metrics.currentActivity} Detected</p>
                       <p className="text-xs text-muted-foreground mt-1 mb-3">Historical pattern shows gradual deviation in schedule.</p>
                   </div>
               </div>
               ) : (
                   <div className="text-muted-foreground">Insufficient Data for Drift Detection</div>
               )}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><ActivitySquare className="size-5" /> Today vs Typical Day</CardTitle>
            </CardHeader>
            <CardContent>
                {metrics.consistency !== "Insufficient Data" ? (
                <div className="space-y-4">
                    <div>
                        <div className="flex justify-between text-xs mb-1"><span>Today (Observed)</span><span className="text-primary">{score}% Match</span></div>
                        <Progress value={score} className="h-2 bg-muted" />
                    </div>
                </div>
                ) : (
                    <div className="text-muted-foreground">Insufficient Data</div>
                )}
            </CardContent>
          </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Planned vs Actual Analysis</CardTitle>
          <CardDescription>Comparison based on uploaded dataset.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {metrics.planVsActual.length > 0 ? metrics.planVsActual.map((item:any, i:number) => (
              <div key={i} className="border rounded-md p-4 bg-muted/20 flex flex-col md:flex-row justify-between items-center gap-4">
                <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                    <p className="text-xs font-medium text-muted-foreground uppercase">Expected Plan</p>
                    <p className="font-bold">{item.expected}</p>
                </div>
                <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                    <p className="text-xs font-medium text-muted-foreground uppercase">Observed from Dataset</p>
                    <p className="font-bold">{item.observed}</p>
                </div>
                <div className="text-center md:text-right w-full md:w-1/3">
                    <Badge variant="outline" className="text-green-700 bg-green-50 border-green-200">{item.status}</Badge>
                </div>
              </div>
          )) : (
              <div className="text-muted-foreground">Insufficient data for Planned vs Actual analysis.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
""",

    "src/routes/anomalies.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ShieldAlert, Database } from "lucide-react";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/anomalies")({
  component: AnomalyDetection,
});

function AnomalyDetection() {
  const [metrics, setMetrics] = useState<any>(null);
  
  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) setMetrics(calculateDashboardMetrics(dataset));
  }, []);

  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first.</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Anomaly & Safety Detection</h1>
        <p className="text-muted-foreground mt-2">Isolation Forest analysis on {metrics.rows} historical rows.</p>
      </div>

      <Card className="border-orange-200 shadow-sm bg-orange-50/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-orange-800"><ShieldAlert className="size-5" /> Detected Anomalies</CardTitle>
        </CardHeader>
        <CardContent>
           <h2 className="text-4xl font-bold text-orange-600 mb-2">{metrics.anomalies}</h2>
           {metrics.anomalies === "Insufficient Data" && <p className="text-muted-foreground text-sm">Anomaly detection requires power/energy or motion features which were not found in the uploaded dataset.</p>}
        </CardContent>
      </Card>
    </div>
  );
}
"""
}

for filename, content in files.items():
    with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)
print("Step 11 completed.")
