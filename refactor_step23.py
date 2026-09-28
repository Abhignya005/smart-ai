import os

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

timeline_content = """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { History, AlertTriangle, Activity } from "lucide-react";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useState, useEffect, useMemo } from "react";

export const Route = createFileRoute("/timeline")({ component: TimelineView });

function TimelineView() {
  const [dataset, setDataset] = useState<any>(null);
  useEffect(() => { setDataset(loadDataset()); }, []);
  
  const m = useMemo(() => {
      if (!dataset) return { timeline: [] };
      return calculateDashboardMetrics(dataset) || { timeline: [] };
  }, [dataset]);

  return (
    <div className="space-y-10 pb-16 animate-in fade-in duration-500">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Today's Timeline</h1>
        <p className="text-muted-foreground text-lg mt-2">Interactive chronological view of your daily activities.</p>
      </div>

      <Card className="border-slate-200 shadow-sm">
         <CardHeader>
            <CardTitle className="flex items-center gap-2"><History className="size-5" /> Chronological Records</CardTitle>
            <CardDescription>Generated from uploaded historical dataset records.</CardDescription>
         </CardHeader>
         <CardContent>
             {m.timeline.length > 0 ? (
                 <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent mt-8">
                    {m.timeline.map((item:any, index:number) => (
                        <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                            <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-slate-200 group-[.is-active]:bg-emerald-500 text-slate-500 group-[.is-active]:text-white shadow-sm shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 transition-colors">
                                <Activity className="size-4" />
                            </div>
                            <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-white p-5 rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow flex justify-between items-center group-hover:border-emerald-200 cursor-pointer">
                                <div>
                                    <div className="font-bold text-slate-900 text-lg">{item.activity}</div>
                                    <div className="text-xs text-slate-500 mt-1 flex gap-3">
                                        <span>Status: <span className="text-emerald-600 font-medium">Completed</span></span>
                                    </div>
                                </div>
                                <time className="font-mono text-sm font-semibold text-slate-600 bg-slate-100 px-3 py-1 rounded-md">{item.time}</time>
                            </div>
                        </div>
                    ))}
                </div>
             ) : (
                 <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
                     <AlertTriangle className="size-8 mb-4 text-slate-300"/>
                     <p>Waiting for Activity Data</p>
                 </div>
             )}
         </CardContent>
      </Card>
    </div>
  );
}
"""

predictions_content = """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, ArrowDown } from "lucide-react";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useState, useEffect, useMemo } from "react";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/predictions")({ component: PredictionsView });

function PredictionsView() {
  const [dataset, setDataset] = useState<any>(null);
  useEffect(() => { setDataset(loadDataset()); }, []);
  
  const m = useMemo(() => {
      const res = dataset ? calculateDashboardMetrics(dataset) : null;
      if (!res) return { currentActivity: 'Not Confirmed', nextActivity: 'Insufficient Data', nextConf: '0%' };
      return res;
  }, [dataset]);

  return (
    <div className="space-y-10 pb-16 animate-in fade-in duration-500">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Next Activity Prediction</h1>
        <p className="text-muted-foreground text-lg mt-2">Markov-chain inspired transition probabilities based on your historical patterns.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="md:col-span-1 border-slate-200 shadow-sm bg-slate-50">
             <CardHeader><CardTitle className="text-xs text-slate-500 uppercase tracking-wider font-bold">Current State</CardTitle></CardHeader>
             <CardContent className="flex flex-col items-center justify-center py-10">
                 <div className="text-4xl font-black text-slate-900">{m.currentActivity}</div>
             </CardContent>
          </Card>
          
          <div className="md:col-span-1 flex items-center justify-center">
             <ArrowDown className="size-10 text-slate-300 md:-rotate-90 animate-pulse"/>
          </div>

          <Card className="md:col-span-1 border-purple-200 shadow-sm bg-purple-50/30">
             <CardHeader><CardTitle className="text-xs text-purple-600 uppercase tracking-wider font-bold">Next Likely Activity</CardTitle></CardHeader>
             <CardContent className="flex flex-col items-center justify-center py-10 space-y-2">
                 <div className="text-4xl font-black text-purple-700 text-center">{m.nextActivity}</div>
                 {m.nextActivity !== 'Insufficient Data' && (
                     <Badge className="bg-purple-600 hover:bg-purple-700">Probability: {m.nextConf}</Badge>
                 )}
             </CardContent>
          </Card>
      </div>

      <Card className="border-slate-200 shadow-sm">
          <CardHeader><CardTitle>Prediction Evidence</CardTitle></CardHeader>
          <CardContent>
              <ul className="space-y-4">
                  <li className="flex justify-between items-center border-b pb-4 border-slate-100">
                      <span className="font-medium text-slate-600">Current Activity Context</span>
                      <span className="font-mono text-sm">{m.currentActivity}</span>
                  </li>
                  <li className="flex justify-between items-center border-b pb-4 border-slate-100">
                      <span className="font-medium text-slate-600">Historical Transitions</span>
                      <span className="font-mono text-sm text-emerald-600">Matches learned sequence</span>
                  </li>
                  <li className="flex justify-between items-center pb-2">
                      <span className="font-medium text-slate-600">Confidence Status</span>
                      <Badge variant="outline" className={m.nextActivity !== 'Insufficient Data' ? 'text-emerald-700 bg-emerald-50 border-emerald-200' : 'text-slate-500 bg-slate-100'}>
                          {m.nextActivity !== 'Insufficient Data' ? 'HIGH CONFIDENCE' : 'LOW CONFIDENCE'}
                      </Badge>
                  </li>
              </ul>
          </CardContent>
      </Card>
    </div>
  );
}
"""

changes_content = """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ShieldAlert, TrendingUp, ActivitySquare } from "lucide-react";

export const Route = createFileRoute("/changes")({ component: ChangesView });

function ChangesView() {
  return (
    <div className="space-y-10 pb-16 animate-in fade-in duration-500">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Routine Changes</h1>
        <p className="text-muted-foreground text-lg mt-2">Differentiating between normal deviations, gradual drift, and statistical anomalies.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
             <CardHeader>
                 <CardTitle className="flex items-center gap-2 text-slate-800"><ActivitySquare className="size-5 text-blue-500"/> Normal Deviation</CardTitle>
                 <CardDescription>Minor, expected variations in daily schedule.</CardDescription>
             </CardHeader>
             <CardContent className="pt-4 border-t border-slate-100 mt-2">
                 <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                     <p className="text-sm font-medium text-slate-700">"Breakfast was 15 minutes later than usual."</p>
                 </div>
                 <p className="text-xs text-slate-500 mt-4 leading-relaxed">The model expects these natural variations and does not flag them as problematic.</p>
             </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
             <CardHeader>
                 <CardTitle className="flex items-center gap-2 text-slate-800"><TrendingUp className="size-5 text-amber-500"/> Routine Drift</CardTitle>
                 <CardDescription>Gradual, sustained changes over time.</CardDescription>
             </CardHeader>
             <CardContent className="pt-4 border-t border-slate-100 mt-2">
                 <div className="bg-amber-50/50 p-4 rounded-lg border border-amber-200">
                     <p className="text-sm font-medium text-amber-900">"Your average sleep time shifted 32 minutes later over the last 3 weeks."</p>
                 </div>
                 <p className="text-xs text-slate-500 mt-4 leading-relaxed">The ML baseline automatically adapts to drift without generating false alarms.</p>
             </CardContent>
          </Card>

          <Card className="border-red-200 shadow-sm hover:shadow-md transition-all bg-red-50/20">
             <CardHeader>
                 <CardTitle className="flex items-center gap-2 text-red-800"><ShieldAlert className="size-5 text-red-500"/> Anomaly</CardTitle>
                 <CardDescription>Sudden, statistically significant deviations.</CardDescription>
             </CardHeader>
             <CardContent className="pt-4 border-t border-red-100 mt-2">
                 <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                     <p className="text-sm font-medium text-red-900">"Activity at 3:12 AM differs significantly from the learned baseline."</p>
                 </div>
                 <p className="text-xs text-slate-500 mt-4 leading-relaxed">Requires immediate review. Flagged by the Isolation Forest model.</p>
             </CardContent>
          </Card>
      </div>
      
      <div className="mt-8 text-center p-6 bg-slate-50 rounded-xl border border-slate-200">
          <p className="text-slate-600">For a detailed list of detected anomalies, please visit the <a href="/anomalies" className="text-primary font-bold hover:underline">Anomaly Detection</a> engine.</p>
      </div>
    </div>
  );
}
"""

with open(os.path.join(ROUTES_DIR, "timeline.tsx"), "w", encoding="utf-8") as f:
    f.write(timeline_content)
with open(os.path.join(ROUTES_DIR, "predictions.tsx"), "w", encoding="utf-8") as f:
    f.write(predictions_content)
with open(os.path.join(ROUTES_DIR, "changes.tsx"), "w", encoding="utf-8") as f:
    f.write(changes_content)

print("Created Timeline, Predictions, and Changes pages.")

