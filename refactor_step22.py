import os

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

index_content = """import { createFileRoute } from "@tanstack/react-router";
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
"""

privacy_content = """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ShieldCheck, Check } from "lucide-react";

export const Route = createFileRoute("/privacy")({ component: PrivacyCenter });

function PrivacyCenter() {
  return (
    <div className="space-y-10 pb-16 animate-in fade-in duration-500">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Privacy Center</h1>
        <p className="text-muted-foreground text-lg mt-2">How PersonaSense AI protects your personal data.</p>
      </div>

      <Card className="bg-emerald-50/50 border-emerald-200 shadow-sm">
          <CardHeader>
              <CardTitle className="flex items-center gap-2 text-emerald-800"><ShieldCheck className="size-6"/> Privacy by Design</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">No camera required</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">No microphone required</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">No facial recognition</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">No wearable required</span></div>
              </div>
              <div className="space-y-3">
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">No live IoT connection</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">Historical dataset analysis only</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">User-controlled uploaded data</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">Explainable ML predictions</span></div>
              </div>
          </CardContent>
      </Card>

      <Card className="shadow-sm">
          <CardHeader>
              <CardTitle>What data is being analyzed?</CardTitle>
          </CardHeader>
          <CardContent>
              <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                  The platform uses mathematical models to find patterns in anonymous ambient data. 
                  These are simply columns in a CSV file, not live connections to your house.
              </p>
              <div className="flex flex-wrap gap-2">
                  {['Timestamp', 'Room', 'Motion', 'Light', 'Door Status', 'Power (kW)', 'Activity Label'].map(f => (
                      <div key={f} className="px-3 py-1.5 bg-slate-100 rounded-md border border-slate-200 text-sm font-medium text-slate-700">{f}</div>
                  ))}
              </div>
              <p className="text-xs text-slate-400 mt-6 font-bold uppercase tracking-widest text-center">NOT A SMART HOME CONTROL SYSTEM</p>
          </CardContent>
      </Card>
    </div>
  );
}
"""

with open(os.path.join(ROUTES_DIR, "index.tsx"), "w", encoding="utf-8") as f:
    f.write(index_content)
with open(os.path.join(ROUTES_DIR, "privacy.tsx"), "w", encoding="utf-8") as f:
    f.write(privacy_content)

print("Created new Index and Privacy pages.")
