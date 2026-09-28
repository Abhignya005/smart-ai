import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, TrendingUp, History, ShieldAlert, Zap } from "lucide-react";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useState, useEffect, useMemo } from "react";

export const Route = createFileRoute("/")({ component: DashboardOverview });

function DashboardOverview() {
  const [dataset, setDataset] = useState<any>(null);
  useEffect(() => { setDataset(loadDataset()); }, []);
  
  const m = useMemo(() => {
      const res = dataset ? calculateDashboardMetrics(dataset) : null;
      if (!res) return { isEmpty: true, rows: 0, consistency: '0%', anomalies: '0', currentActivity: 'Not Confirmed', currentConf: '0%', nextActivity: 'Insufficient Data', nextConf: '0%', timeline: [] };
      return res;
  }, [dataset]);

  const dateRange = dataset?.data?.length > 0 && dataset.headers.includes('Time') ? 
      `${dataset.data[0]['Time'].split(' ')[0]} to ${dataset.data[dataset.data.length-1]['Time'].split(' ')[0]}` : 
      'Historical Data';

  return (
    <div className="space-y-10 pb-16 animate-in fade-in duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Good evening</h1>
        <p className="text-muted-foreground text-lg">Here's what your routine looks like based on historical data.</p>
        <div className="mt-2 inline-flex items-center gap-4 text-xs font-medium bg-slate-100/50 p-3 rounded-lg border border-slate-200 w-fit">
            <span className="text-slate-500">Dataset: <span className="text-slate-900">{dateRange}</span></span>
            <span className="text-slate-300">|</span>
            <span className="text-slate-500">Records: <span className="text-slate-900">{m.rows}</span></span>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-slate-500 uppercase tracking-wider font-bold">Current Activity</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-black text-slate-900">{m.currentActivity}</div>
            <p className="text-sm font-medium text-emerald-600 mt-1">Confidence: {m.currentConf}</p>
          </CardContent>
        </Card>
        
        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-slate-500 uppercase tracking-wider font-bold">Routine Score</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-black text-slate-900">{m.consistency}</div>
            <p className="text-sm font-medium text-slate-500 mt-1">Compared to typical routine</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-slate-500 uppercase tracking-wider font-bold">Next Activity</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-black text-purple-700">{m.nextActivity}</div>
            <p className="text-sm font-medium text-purple-600/80 mt-1">Probability: {m.nextConf}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all bg-orange-50/30">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-slate-500 uppercase tracking-wider font-bold">Deviations</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-black text-orange-600">{m.anomalies} Detected</div>
            <p className="text-sm font-medium text-orange-600/80 mt-1">Requires review</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
