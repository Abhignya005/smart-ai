import { createFileRoute } from "@tanstack/react-router";
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
