import os
import re

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

file_content = """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { 
  Database, Activity, TrendingUp, History, ShieldAlert, Zap, 
  HelpCircle, Check, X, ShieldCheck, Info, MapPin, Clock, Calendar 
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useState, useEffect, useMemo } from "react";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { toast } from "sonner";

export const Route = createFileRoute("/")({
  component: UnifiedDashboard,
});

function UnifiedDashboard() {
  const [dataset, setDataset] = useState<any>(null);
  
  useEffect(() => {
      setDataset(loadDataset());
  }, []);

  return (
    <div className="space-y-12 pb-16">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight">SmartHome Analytics Dashboard</h1>
        <p className="text-muted-foreground mt-2 text-lg">Unified Privacy-Preserving Machine Learning Intelligence.</p>
      </div>

      <DashboardSummary dataset={dataset} />
      
      <div className="border-t border-slate-200 my-8 pt-8">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2"><Activity className="text-primary"/> Activity & Routine Intelligence</h2>
        <RoutineSection dataset={dataset} />
      </div>

      <div className="border-t border-slate-200 my-8 pt-8">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2"><ShieldAlert className="text-orange-500"/> Anomaly & Safety Detection</h2>
        <AnomalySection dataset={dataset} />
      </div>
      
      <div className="border-t border-slate-200 my-8 pt-8">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2"><Zap className="text-blue-500"/> Energy Intelligence</h2>
        <EnergySection dataset={dataset} />
      </div>
    </div>
  );
}

// ==========================================
// 1. DASHBOARD SUMMARY
// ==========================================
function DashboardSummary({ dataset }: { dataset: any }) {
  const m = useMemo(() => calculateDashboardMetrics(dataset), [dataset]);
  
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card className={m.isEmpty ? "opacity-60 bg-muted/20" : ""}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Dataset Status</CardTitle>
          <Database className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{m.rows}</div>
          <p className="text-xs text-muted-foreground">Rows analyzed</p>
        </CardContent>
      </Card>
      
      <Card className={m.isEmpty ? "opacity-60 bg-muted/20" : ""}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Routine Consistency</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${m.isEmpty ? 'text-lg text-muted-foreground' : ''}`}>{m.consistency}</div>
          <p className="text-xs text-muted-foreground">Historical pattern match</p>
        </CardContent>
      </Card>
      
      <Card className={m.isEmpty ? "opacity-60 bg-muted/20" : ""}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Anomalies</CardTitle>
          <ShieldAlert className="h-4 w-4 text-orange-500" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${m.isEmpty ? 'text-lg text-muted-foreground' : 'text-orange-600'}`}>{m.anomalies}</div>
          {m.anomalies === "Insufficient Data" ? 
              <p className="text-xs text-muted-foreground">Needs Power/Energy feature.</p> :
              <p className="text-xs text-muted-foreground">Awaiting review</p>
          }
        </CardContent>
      </Card>
      
      <Card className={m.isEmpty ? "opacity-60 bg-muted/20" : ""}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Peak Energy</CardTitle>
          <Zap className="h-4 w-4 text-blue-500" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${m.isEmpty ? 'text-lg text-muted-foreground' : 'text-blue-600'}`}>{m.peakEnergy}</div>
          {m.peakEnergy === "Not Available" ? 
              <p className="text-xs text-muted-foreground">No power feature found.</p> :
              <p className="text-xs text-muted-foreground">Dynamic peak observation</p>
          }
        </CardContent>
      </Card>
    </div>
  );
}


// ==========================================
// 2. ROUTINE SECTION
// ==========================================
function RoutineSection({ dataset }: { dataset: any }) {
  const m = useMemo(() => calculateDashboardMetrics(dataset), [dataset]);
  if (!dataset || dataset.data.length === 0) return <div className="text-center p-8 text-muted-foreground">No dataset available for Activity & Routine Intelligence.</div>;
  
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-6">
              <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><Activity className="size-5" /> Current Activity</CardTitle></CardHeader>
                  <CardContent>
                      <div className="flex justify-between items-center">
                          <div>
                              <h2 className="text-3xl font-bold text-primary">{m.currentActivity}</h2>
                              <p className="text-sm text-muted-foreground">Detected at: {m.lastTimestamp}</p>
                          </div>
                          {m.currentActivity !== 'Not Confirmed' && (
                              <div className="text-right"><p className="text-sm font-semibold">Confidence</p><p className="text-xl font-bold">{m.currentConf}</p></div>
                          )}
                      </div>
                  </CardContent>
              </Card>
              <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><TrendingUp className="size-5" /> Next Activity Prediction</CardTitle></CardHeader>
                  <CardContent>
                       <div className="flex justify-between items-center">
                          <div><h2 className="text-3xl font-bold text-purple-600">{m.nextActivity}</h2></div>
                          {m.nextActivity !== 'Insufficient Data' && (
                              <div className="text-right"><p className="text-sm font-semibold">Probability</p><p className="text-xl font-bold">{m.nextConf}</p></div>
                          )}
                      </div>
                  </CardContent>
              </Card>
          </div>
          <Card>
             <CardHeader><CardTitle className="flex items-center gap-2"><History className="size-5" /> Today's Timeline</CardTitle><CardDescription>Generated from uploaded historical dataset.</CardDescription></CardHeader>
             <CardContent>
                 <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent max-h-[300px] overflow-y-auto">
                    {m.timeline.map((item:any, index:number) => (
                        <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                            <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-primary text-primary-foreground shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2"><Activity className="size-4" /></div>
                            <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-card p-4 rounded border shadow flex justify-between items-center">
                                <div className="font-bold text-primary">{item.activity}</div>
                                <time className="font-mono text-xs text-muted-foreground">{item.time}</time>
                            </div>
                        </div>
                    ))}
                </div>
             </CardContent>
          </Card>
      </div>
      
      {m.planVsActual.length > 0 && (
          <Card>
              <CardHeader><CardTitle>Planned vs Actual Analysis</CardTitle></CardHeader>
              <CardContent>
                  {m.planVsActual.map((item:any, i:number) => (
                      <div key={i} className="border rounded-md p-4 bg-muted/20 flex flex-col md:flex-row justify-between items-center gap-4">
                        <div className="space-y-1 text-center md:text-left w-full md:w-1/3"><p className="text-xs font-medium text-muted-foreground uppercase">Expected Plan</p><p className="font-bold">{item.expected}</p></div>
                        <div className="space-y-1 text-center md:text-left w-full md:w-1/3"><p className="text-xs font-medium text-muted-foreground uppercase">Observed from Dataset</p><p className="font-bold">{item.observed}</p></div>
                        <div className="text-center md:text-right w-full md:w-1/3"><Badge variant="outline" className="text-green-700 bg-green-50 border-green-200">{item.status}</Badge></div>
                      </div>
                  ))}
              </CardContent>
          </Card>
      )}
    </div>
  );
}

// ==========================================
// 3. ANOMALY SECTION
// ==========================================
function AnomalySection({ dataset }: { dataset: any }) {
  const [selectedAnomaly, setSelectedAnomaly] = useState<any>(null);
  
  const anomalyData = useMemo(() => {
      if (!dataset || dataset.data.length < 5) return null;
      const data = dataset.data;
      const timeCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('time') || hd.toLowerCase().includes('date'));
      const actCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('activity'));
      const roomCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('room'));
      const powerCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('power') || hd.toLowerCase().includes('kw'));

      let list: any[] = [];
      const parseMins = (t: string) => {
          if (!t) return 0;
          const p = t.split(' ');
          const tt = p.length > 1 ? p[1] : p[0];
          const [hh, mm] = tt.split(':').map(Number);
          return (isNaN(hh) ? 0 : hh) * 60 + (isNaN(mm) ? 0 : mm);
      };
      
      let typicalTimes: any = {};
      if (actCol && timeCol) {
          data.forEach((r:any) => {
              const act = r[actCol];
              if (act) {
                  if (!typicalTimes[act]) typicalTimes[act] = [];
                  typicalTimes[act].push(parseMins(r[timeCol]));
              }
          });
          Object.keys(typicalTimes).forEach(k => {
              const arr = typicalTimes[k];
              typicalTimes[k] = arr.reduce((a:number,b:number)=>a+b,0) / arr.length;
          });
      }

      data.forEach((r:any, i:number) => {
          let score = 0;
          let reasons = [];
          
          if (actCol && timeCol && typicalTimes[r[actCol]]) {
              const diff = Math.abs(parseMins(r[timeCol]) - typicalTimes[r[actCol]]);
              if (diff > 180) { score += 2.5; reasons.push("Unusual time for this activity"); }
              else if (diff > 90) { score += 1.0; }
          }
          if (powerCol) {
              const p = parseFloat(r[powerCol]);
              if (!isNaN(p) && p > 3.0) { score += 1.5; reasons.push("Unusually high energy usage"); }
          }
          
          if (score >= 1.0) {
              let sev = score > 2.5 ? "HIGH" : score >= 1.5 ? "MEDIUM" : "LOW";
              const rawTime = timeCol ? r[timeCol] : `Row ${i}`;
              list.push({
                  id: i,
                  time: rawTime.includes(' ') ? rawTime.split(' ')[1] : rawTime,
                  date: rawTime.includes(' ') ? rawTime.split(' ')[0] : '',
                  activity: actCol ? r[actCol] : 'Unknown',
                  room: roomCol ? r[roomCol] : 'Unknown',
                  severity: sev,
                  score: `-${score.toFixed(2)}`,
                  reasons,
                  typicalAct: actCol ? 'Learned Routine' : 'N/A'
              });
          }
      });
      list.sort((a,b) => parseFloat(a.score) - parseFloat(b.score));
      return { list };
  }, [dataset]);

  if (!dataset || !anomalyData) return <div className="text-center p-8 text-muted-foreground">Insufficient data for Anomaly Analysis.</div>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="flex flex-col">
            <CardHeader><CardTitle>Anomaly Timeline</CardTitle></CardHeader>
            <CardContent className="flex-1 overflow-y-auto max-h-[400px]">
                {anomalyData.list.length > 0 ? (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Time</TableHead>
                                <TableHead>Activity</TableHead>
                                <TableHead>Severity</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {anomalyData.list.map((anom:any) => (
                                <TableRow key={anom.id} className="cursor-pointer hover:bg-muted/50" onClick={() => setSelectedAnomaly(anom)}>
                                    <TableCell className="font-mono text-xs whitespace-nowrap">{anom.time}</TableCell>
                                    <TableCell className="font-medium">{anom.activity}</TableCell>
                                    <TableCell>
                                        <Badge variant="outline" className={anom.severity === 'HIGH' ? 'bg-red-50 text-red-700' : anom.severity === 'MEDIUM' ? 'bg-orange-50 text-orange-700' : 'bg-amber-50 text-amber-700'}>{anom.severity}</Badge>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                ) : (
                    <div className="text-center p-8 text-muted-foreground">No anomalies detected.</div>
                )}
            </CardContent>
        </Card>
        
        <Card className="flex flex-col">
             <CardHeader><CardTitle>Anomaly Details</CardTitle></CardHeader>
             <CardContent>
                  {selectedAnomaly ? (
                      <div className="space-y-4 animate-in fade-in">
                          <div className="flex justify-between items-start border-b pb-4">
                              <div>
                                  <h3 className="font-bold text-lg">{selectedAnomaly.time} &mdash; {selectedAnomaly.activity}</h3>
                                  <p className="text-sm text-muted-foreground">Room: {selectedAnomaly.room}</p>
                              </div>
                              <div className="text-right">
                                  <Badge variant="outline" className={selectedAnomaly.severity === 'HIGH' ? 'bg-red-50 text-red-700' : 'bg-orange-50 text-orange-700'}>{selectedAnomaly.severity}</Badge>
                                  <p className="text-xs font-mono mt-1 text-muted-foreground">Score: {selectedAnomaly.score}</p>
                              </div>
                          </div>
                          <div className="space-y-2">
                              <p className="text-xs font-semibold uppercase text-muted-foreground">Why Unusual</p>
                              <ul className="list-disc pl-5 text-sm space-y-1">
                                  {selectedAnomaly.reasons.map((r:string, i:number) => <li key={i}>{r}</li>)}
                              </ul>
                          </div>
                      </div>
                  ) : (
                      <div className="h-full flex items-center justify-center text-sm text-muted-foreground py-12">Select an anomaly from the timeline.</div>
                  )}
             </CardContent>
        </Card>
    </div>
  );
}

// ==========================================
// 4. ENERGY SECTION
// ==========================================
function EnergySection({ dataset }: { dataset: any }) {
  const energyData = useMemo(() => {
      if (!dataset || dataset.data.length === 0) return null;
      const data = dataset.data;
      const timeCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('time') || hd.toLowerCase().includes('date'));
      const powerCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('power') || hd.toLowerCase().includes('kw') || hd.toLowerCase().includes('energy'));
      if (!powerCol) return null;

      let timeline: any[] = [];
      let max = -Infinity, sum = 0, count = 0;

      data.forEach((r:any) => {
          const p = parseFloat(r[powerCol]);
          if (!isNaN(p)) {
              if (p > max) max = p;
              sum += p;
              count++;
              timeline.push({ time: timeCol ? r[timeCol] : '', power: p });
          }
      });
      if (count === 0) return null;
      return { timeline, max: max.toFixed(2), avg: (sum/count).toFixed(2) };
  }, [dataset]);

  if (!energyData) return <div className="text-center p-8 text-muted-foreground">Insufficient data: Missing power/energy column.</div>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
            <CardHeader><CardTitle>Energy Timeline</CardTitle></CardHeader>
            <CardContent>
                <div className="h-[250px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={energyData.timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <defs>
                                <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/><stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/></linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="time" tickLine={false} axisLine={false} fontSize={12} minTickGap={30} />
                            <YAxis tickLine={false} axisLine={false} fontSize={12} />
                            <Tooltip contentStyle={{ borderRadius: '8px' }} />
                            <Area type="monotone" dataKey="power" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorPower)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
        <Card>
            <CardHeader><CardTitle>Peak vs Average Comparison</CardTitle></CardHeader>
            <CardContent className="space-y-8 pt-6">
                <div className="space-y-2">
                    <div className="flex justify-between text-sm font-medium">
                        <span>Average Sustained Usage</span>
                        <span className="text-blue-600">{energyData.avg} kW</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-3">
                        <div className="bg-blue-500 h-3 rounded-full" style={{ width: `${Math.min((parseFloat(energyData.avg)/parseFloat(energyData.max))*100, 100)}%` }}></div>
                    </div>
                </div>
                <div className="space-y-2">
                    <div className="flex justify-between text-sm font-medium">
                        <span>Maximum Spike (Peak)</span>
                        <span className="text-red-600">{energyData.max} kW</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-3">
                        <div className="bg-red-500 h-3 rounded-full" style={{ width: '100%' }}></div>
                    </div>
                </div>
            </CardContent>
        </Card>
    </div>
  );
}
"""

with open(os.path.join(ROUTES_DIR, "index.tsx"), "w", encoding="utf-8") as f:
    f.write(file_content)

print("index.tsx merged into unified massive dashboard.")
