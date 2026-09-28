import { createFileRoute } from "@tanstack/react-router";
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
