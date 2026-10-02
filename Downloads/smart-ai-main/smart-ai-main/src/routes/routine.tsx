import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { TrendingUp, Activity, ActivitySquare, ShieldAlert, History, Database } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { loadDataset, getOrFetchDataset, onDatasetUpdate } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useState, useEffect } from "react";

export const Route = createFileRoute("/routine")({
  component: RoutineDiscovery,
});

function RoutineDiscovery() {
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

  if (!metrics) {
      return (
          <div className="flex flex-col items-center justify-center h-[60vh] space-y-4">
              <Database className="size-12 text-muted-foreground opacity-50" />
              <p className="text-muted-foreground">Please upload a dataset to view routine insights.</p>
          </div>
      );
  }

  const { rows, rawRowCount, consistency, currentActivity, currentConf, nextActivity, nextConf, timeline, driftInfo, insights, planVsActual } = metrics;

  return (
    <div className="space-y-6 pb-16">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Routine Discovery</h1>
          <p className="text-muted-foreground mt-2">Personal Routine Learning powered by chronological historical data.</p>
        </div>
        <div className="text-right">
            <Badge variant="outline" className="bg-primary/5 text-primary text-xs py-1">
                Data Source: Calculated from uploaded dataset — {rows} rows
            </Badge>
        </div>
      </div>

      {/* TOP KPI ROW */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Daily Routine Score</CardTitle></CardHeader>
              <CardContent>
                  <div className={`text-2xl font-bold ${consistency === 'Insufficient Data' ? 'text-lg text-muted-foreground' : 'text-primary'}`}>{consistency}</div>
                  <p className="text-xs text-muted-foreground">Historical timing match</p>
              </CardContent>
          </Card>
          <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Current Activity</CardTitle></CardHeader>
              <CardContent>
                  <div className={`text-2xl font-bold truncate ${currentActivity === 'Not Confirmed' ? 'text-lg text-muted-foreground' : 'text-primary'}`}>{currentActivity}</div>
                  <p className="text-xs text-muted-foreground">Confidence: {currentConf}</p>
              </CardContent>
          </Card>
          <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Next Prediction</CardTitle></CardHeader>
              <CardContent>
                  <div className={`text-2xl font-bold truncate ${nextActivity.includes('Insufficient') || nextActivity.includes('Low') ? 'text-lg text-muted-foreground' : 'text-purple-600'}`}>{nextActivity}</div>
                  <p className="text-xs text-muted-foreground">Probability: {nextConf}</p>
              </CardContent>
          </Card>
          <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Routine Drift</CardTitle></CardHeader>
              <CardContent>
                  <div className={`text-xl font-bold ${driftInfo.status === 'Insufficient Data' ? 'text-lg text-muted-foreground' : driftInfo.status === 'Stable' ? 'text-green-600' : 'text-orange-600'}`}>{driftInfo.status}</div>
                  <p className="text-xs text-muted-foreground line-clamp-1">{driftInfo.text}</p>
              </CardContent>
          </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="md:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><TrendingUp className="size-5" /> Routine Drift Analysis</CardTitle>
              <CardDescription>Chronological baseline tracking.</CardDescription>
            </CardHeader>
            <CardContent>
               <div className="p-4 border rounded-md bg-muted/10 flex flex-col gap-2">
                   <div className="flex justify-between items-start">
                       <p className="font-semibold text-sm">Status</p>
                       <Badge variant="outline" className={driftInfo.status === 'Insufficient Data' ? '' : driftInfo.status === 'Stable' ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}>
                           {driftInfo.status}
                       </Badge>
                   </div>
                   <p className="text-sm text-muted-foreground">{driftInfo.text}</p>
               </div>
            </CardContent>
          </Card>
          
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><ActivitySquare className="size-5" /> Personal Routine Insights</CardTitle>
              <CardDescription>Typical times computed via density clustering (ignoring outliers).</CardDescription>
            </CardHeader>
            <CardContent>
                {insights.comparison.length > 0 ? (
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        {insights.comparison.map((c:any, i:number) => (
                             <div key={i} className="border p-3 rounded-md bg-card shadow-sm">
                                 <p className="text-xs text-muted-foreground truncate">Typical {c.activity}</p>
                                 <p className="text-lg font-bold">{c.typical}</p>
                             </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-muted-foreground">Insufficient Data: Cannot calculate meaningful typical times.</div>
                )}
            </CardContent>
          </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
             <CardHeader>
                <CardTitle>Today vs Typical Day</CardTitle>
             </CardHeader>
             <CardContent>
                 {insights.comparison.length > 0 && insights.comparison.some((c:any) => c.today !== '--:--') ? (
                     <div className="overflow-x-auto">
                     <Table>
                         <TableHeader>
                             <TableRow>
                                 <TableHead>Activity</TableHead>
                                 <TableHead>Typical Time</TableHead>
                                 <TableHead>Latest Observed</TableHead>
                                 <TableHead>Variance</TableHead>
                             </TableRow>
                         </TableHeader>
                         <TableBody>
                             {insights.comparison.filter((c:any)=>c.today !== '--:--').map((item:any, i:number) => (
                                 <TableRow key={i}>
                                     <TableCell className="font-medium">{item.activity}</TableCell>
                                     <TableCell>{item.typical}</TableCell>
                                     <TableCell>{item.today}</TableCell>
                                     <TableCell>
                                         <Badge variant="outline" className={
                                             item.status === 'Late' ? 'text-orange-600 bg-orange-50' : 
                                             item.status === 'Early' ? 'text-blue-600 bg-blue-50' : 
                                             'text-green-600 bg-green-50'
                                         }>
                                             {item.diffMins > 0 ? '+' : ''}{item.diffMins} min ({item.status})
                                         </Badge>
                                     </TableCell>
                                 </TableRow>
                             ))}
                         </TableBody>
                     </Table>
                     </div>
                 ) : (
                     <div className="text-muted-foreground">Insufficient recent data to build comparison table.</div>
                 )}
             </CardContent>
          </Card>

          <Card className="h-full">
             <CardHeader>
                <CardTitle className="flex items-center gap-2"><History className="size-5" /> Activity Timeline</CardTitle>
                <CardDescription>Chronologically extracted from dataset.</CardDescription>
             </CardHeader>
             <CardContent>
                 {timeline.length > 0 ? (
                     <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-slate-200 pl-8 overflow-y-auto max-h-[400px] pr-2">
                        {timeline.slice(-20).map((item:any, index:number) => (
                            <div key={index} className="relative mb-6">
                                <div className="absolute -left-10 mt-1 flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground border-2 border-background">
                                    <Activity className="size-3" />
                                </div>
                                <div className="bg-card p-3 rounded-md border shadow-sm">
                                    <div className="flex items-center justify-between mb-1">
                                        <div className="font-bold text-primary">{item.activity}</div>
                                        <time className="font-mono text-xs text-muted-foreground">{item.date} {item.time}</time>
                                    </div>
                                    <div className="flex justify-between items-center mt-2 text-[10px] text-muted-foreground uppercase">
                                        <span>Status: {item.duration}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                 ) : (
                     <div className="text-muted-foreground">Insufficient Activity Data in dataset.</div>
                 )}
             </CardContent>
          </Card>
      </div>
    </div>
  );
}
