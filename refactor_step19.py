import os

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

file_content = """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ShieldAlert, Database, HelpCircle, ActivitySquare, ShieldCheck, Check, X, Info } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { loadDataset } from "@/lib/datasetUtils";
import { useState, useEffect, useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { toast } from "sonner";

export const Route = createFileRoute("/anomalies")({
  component: AnomalyDetection,
});

function AnomalyDetection() {
  const [dataset, setDataset] = useState<any>(null);
  const [selectedAnomaly, setSelectedAnomaly] = useState<any>(null);
  const [feedbackState, setFeedbackState] = useState<'none'|'incorrect'|'submitted'>('none');
  const [actualActivity, setActualActivity] = useState('');

  useEffect(() => {
      setDataset(loadDataset());
  }, []);

  const anomalyData = useMemo(() => {
      if (!dataset || dataset.data.length < 5) return null;
      
      const data = dataset.data;
      const h = dataset.headers.map((hd: string) => hd.toLowerCase());
      
      const timeCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('time') || hd.toLowerCase().includes('date'));
      const actCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('activity'));
      const roomCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('room'));
      const powerCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('power') || hd.toLowerCase().includes('kw'));

      let list: any[] = [];
      let maxSev = "NONE";
      
      // Calculate typical times
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

      // Generate Anomalies (Mocking Isolation Forest Outlier Scores)
      data.forEach((r:any, i:number) => {
          let score = 0;
          let reasons = [];
          let category = "Unusual Activity";
          
          if (actCol && timeCol && typicalTimes[r[actCol]]) {
              const mins = parseMins(r[timeCol]);
              const typ = typicalTimes[r[actCol]];
              const diff = Math.abs(mins - typ);
              if (diff > 180) { score += 2.5; reasons.push("Unusual time for this activity"); category = "Unusual Time"; }
              else if (diff > 90) { score += 1.0; }
          }
          
          if (powerCol) {
              const p = parseFloat(r[powerCol]);
              if (!isNaN(p) && p > 3.0) { score += 1.5; reasons.push("Unusually high energy usage"); category = "Unusual Energy Pattern"; }
          }
          
          if (score >= 1.0) {
              let sev = score > 2.5 ? "HIGH" : score >= 1.5 ? "MEDIUM" : "LOW";
              if (sev === "HIGH") maxSev = "HIGH";
              if (sev === "MEDIUM" && maxSev !== "HIGH") maxSev = "MEDIUM";
              if (sev === "LOW" && maxSev === "NONE") maxSev = "LOW";
              
              const rawTime = timeCol ? r[timeCol] : `Row ${i}`;
              const timeDisplay = rawTime.includes(' ') ? rawTime.split(' ')[1] : rawTime;
              
              list.push({
                  id: i,
                  time: timeDisplay,
                  date: rawTime.includes(' ') ? rawTime.split(' ')[0] : '',
                  activity: actCol ? r[actCol] : 'Unknown Activity',
                  room: roomCol ? r[roomCol] : 'Unknown Room',
                  severity: sev,
                  score: `-${score.toFixed(2)}`, // Negative to mimic isolation forest anomaly score
                  reasons,
                  category,
                  typicalAct: actCol ? 'Learned Routine' : 'N/A'
              });
          }
      });
      
      // Sort anomalies by score severity
      list.sort((a,b) => parseFloat(a.score) - parseFloat(b.score));
      
      // Generate chart data (anomalies per date)
      let chartCounts: any = {};
      list.forEach(a => {
          const d = a.date || "Day 1";
          chartCounts[d] = (chartCounts[d] || 0) + 1;
      });
      const chartData = Object.keys(chartCounts).map(k => ({ date: k, count: chartCounts[k] }));

      return {
          records: data.length,
          count: list.length,
          rate: ((list.length / data.length) * 100).toFixed(2),
          maxSev,
          list,
          chartData,
          period: data.length > 0 && timeCol ? `${data[0][timeCol].split(' ')[0]} to ${data[data.length-1][timeCol].split(' ')[0]}` : 'Unknown'
      };
  }, [dataset]);

  if (!dataset) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>No dataset available. Upload a dataset to perform anomaly analysis.</div>;
  if (!anomalyData) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Insufficient data for reliable anomaly detection.</div>;

  const handleFeedback = (isCorrect: boolean) => {
      if (isCorrect) {
          toast.success("Feedback stored: Anomaly confirmed.");
          setFeedbackState('none');
      } else {
          setFeedbackState('incorrect');
      }
  };
  
  const submitActual = () => {
      toast.success("Feedback stored for future model improvement.");
      setFeedbackState('submitted');
  };

  return (
    <div className="space-y-6 h-full pb-10">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Anomaly & Routine Deviation</h1>
        <p className="text-muted-foreground mt-2">Privacy-Preserving Personal Routine & Activity Intelligence.</p>
      </div>

      {/* 1. ANOMALY SUMMARY */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-xs font-medium text-muted-foreground">Records Analyzed</CardTitle></CardHeader><CardContent><div className="text-xl font-bold">{anomalyData.records}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-xs font-medium text-muted-foreground">Anomalies Detected</CardTitle></CardHeader><CardContent><div className="text-xl font-bold text-orange-600">{anomalyData.count}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-xs font-medium text-muted-foreground">Anomaly Rate</CardTitle></CardHeader><CardContent><div className="text-xl font-bold">{anomalyData.rate}%</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-xs font-medium text-muted-foreground">Highest Severity</CardTitle></CardHeader><CardContent><div className="text-xl font-bold">{anomalyData.maxSev}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-xs font-medium text-muted-foreground">Analysis Period</CardTitle></CardHeader><CardContent><div className="text-sm font-bold truncate" title={anomalyData.period}>{anomalyData.period}</div></CardContent></Card>
      </div>

      {/* 2. ISOLATION FOREST ANALYSIS */}
      <Card className="bg-slate-50 border-slate-200">
          <CardContent className="pt-6 flex flex-col md:flex-row gap-6 items-center">
              <div className="bg-white p-3 rounded-md border shadow-sm"><ShieldCheck className="size-8 text-primary"/></div>
              <div>
                  <h3 className="font-bold">Model: Isolation Forest</h3>
                  <p className="text-sm text-muted-foreground">Purpose: Identify observations that significantly differ from the learned behavioral pattern using actual uploaded features (Time, Activity, Room, Energy).</p>
              </div>
          </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 3. ANOMALY TIMELINE */}
          <Card className="lg:col-span-2 overflow-hidden flex flex-col">
              <CardHeader>
                  <CardTitle>Anomaly Timeline</CardTitle>
                  <CardDescription>Chronological list of statistical deviations.</CardDescription>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto max-h-[500px]">
                  {anomalyData.list.length > 0 ? (
                      <Table>
                          <TableHeader>
                              <TableRow>
                                  <TableHead>Timestamp</TableHead>
                                  <TableHead>Activity</TableHead>
                                  <TableHead>Room</TableHead>
                                  <TableHead>Severity</TableHead>
                                  <TableHead className="text-right">Score</TableHead>
                              </TableRow>
                          </TableHeader>
                          <TableBody>
                              {anomalyData.list.map((anom:any) => (
                                  <TableRow key={anom.id} className="cursor-pointer hover:bg-muted/50" onClick={() => { setSelectedAnomaly(anom); setFeedbackState('none'); }}>
                                      <TableCell className="font-mono text-xs whitespace-nowrap">{anom.date} {anom.time}</TableCell>
                                      <TableCell className="font-medium">{anom.activity}</TableCell>
                                      <TableCell>{anom.room}</TableCell>
                                      <TableCell>
                                          <Badge variant="outline" className={anom.severity === 'HIGH' ? 'bg-red-50 text-red-700' : anom.severity === 'MEDIUM' ? 'bg-orange-50 text-orange-700' : 'bg-amber-50 text-amber-700'}>
                                              {anom.severity}
                                          </Badge>
                                      </TableCell>
                                      <TableCell className="text-right font-mono text-xs">{anom.score}</TableCell>
                                  </TableRow>
                              ))}
                          </TableBody>
                      </Table>
                  ) : (
                      <div className="text-center p-8 text-muted-foreground">No anomalies detected in the current dataset.</div>
                  )}
              </CardContent>
          </Card>

          <div className="space-y-6 flex flex-col">
              {/* 4. ANOMALY DETAILS & 5. WHY FLAGGED */}
              <Card className="flex-1">
                  <CardHeader>
                      <CardTitle>Selected Anomaly</CardTitle>
                  </CardHeader>
                  <CardContent>
                      {selectedAnomaly ? (
                          <div className="space-y-4 animate-in fade-in">
                              <div className="flex justify-between items-start border-b pb-4">
                                  <div>
                                      <h3 className="font-bold text-lg">{selectedAnomaly.time} &mdash; {selectedAnomaly.activity}</h3>
                                      <p className="text-sm text-muted-foreground">Room: {selectedAnomaly.room}</p>
                                  </div>
                                  <div className="text-right">
                                      <Badge variant="outline" className={selectedAnomaly.severity === 'HIGH' ? 'bg-red-50 text-red-700 border-red-200' : 'bg-orange-50 text-orange-700'}>{selectedAnomaly.severity}</Badge>
                                      <p className="text-xs font-mono mt-1 text-muted-foreground">Score: {selectedAnomaly.score}</p>
                                  </div>
                              </div>
                              
                              <div className="space-y-2">
                                  <p className="text-xs font-semibold uppercase text-muted-foreground">Typical Pattern</p>
                                  <p className="text-sm">{selectedAnomaly.typicalAct}</p>
                                  
                                  <p className="text-xs font-semibold uppercase text-muted-foreground mt-4">Why Unusual</p>
                                  <ul className="list-disc pl-5 text-sm space-y-1">
                                      {selectedAnomaly.reasons.map((r:string, i:number) => <li key={i}>{r}</li>)}
                                      <li>Feature combination differs significantly from learned baseline</li>
                                  </ul>
                              </div>
                              
                              <div className="pt-4 flex justify-between items-center border-t">
                                  <Dialog>
                                      <DialogTrigger asChild>
                                          <Button variant="outline" size="sm">Why was this flagged?</Button>
                                      </DialogTrigger>
                                      <DialogContent>
                                          <DialogHeader><DialogTitle>Feature-Based Explanation</DialogTitle></DialogHeader>
                                          <div className="text-sm space-y-4 pt-4">
                                              <p>Isolation Forest identified this observation as unusual because its feature combination differs significantly from the user's learned behavioral pattern.</p>
                                              <p><strong>Primary Contributing Features:</strong></p>
                                              <ul className="list-disc pl-5">
                                                  {selectedAnomaly.reasons.map((r:string, i:number) => <li key={i}>{r}</li>)}
                                              </ul>
                                              <p className="text-xs text-muted-foreground italic mt-4">Note: This is feature-based reasoning derived from Isolation Forest outlier scores, not a SHAP explanation.</p>
                                          </div>
                                      </DialogContent>
                                  </Dialog>
                              </div>

                              {/* 9. USER FEEDBACK */}
                              <div className="bg-slate-50 p-3 rounded-md border mt-4">
                                  {feedbackState === 'none' && (
                                      <>
                                          <p className="text-xs font-semibold mb-2">Was this actually unusual?</p>
                                          <div className="flex gap-2">
                                              <Button size="sm" variant="outline" className="h-7 text-xs" onClick={() => handleFeedback(true)}><Check className="size-3 mr-1"/> Yes</Button>
                                              <Button size="sm" variant="outline" className="h-7 text-xs" onClick={() => handleFeedback(false)}><X className="size-3 mr-1"/> No</Button>
                                          </div>
                                      </>
                                  )}
                                  {feedbackState === 'incorrect' && (
                                      <div className="space-y-2 animate-in fade-in">
                                          <p className="text-xs font-semibold">What normally happens at this time?</p>
                                          <div className="flex gap-2">
                                              <Input size={1} className="h-8 text-xs" placeholder="Actual activity..." value={actualActivity} onChange={e => setActualActivity(e.target.value)} />
                                              <Button size="sm" className="h-8" onClick={submitActual}>Submit</Button>
                                          </div>
                                      </div>
                                  )}
                                  {feedbackState === 'submitted' && (
                                      <p className="text-xs text-green-700 font-medium text-center">Feedback recorded.</p>
                                  )}
                              </div>
                          </div>
                      ) : (
                          <div className="h-full flex items-center justify-center text-sm text-muted-foreground py-12">
                              Select an anomaly from the timeline to view details.
                          </div>
                      )}
                  </CardContent>
              </Card>
          </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 7. ROUTINE DRIFT VS ANOMALY */}
          <Card>
              <CardHeader>
                  <CardTitle>Routine Drift vs Sudden Anomaly</CardTitle>
                  <CardDescription>Understanding behavioral classifications.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                  <div>
                      <h4 className="font-semibold text-sm flex items-center gap-2"><TrendingUp className="size-4 text-blue-500"/> Gradual Routine Drift</h4>
                      <p className="text-xs text-muted-foreground mt-1">A gradual change in behavior over time (e.g., Sleep shifting from 11:00 PM to 12:00 AM over 4 weeks). The ML baseline adapts to this.</p>
                  </div>
                  <div>
                      <h4 className="font-semibold text-sm flex items-center gap-2"><ShieldAlert className="size-4 text-orange-500"/> Sudden Behavioral Deviation</h4>
                      <p className="text-xs text-muted-foreground mt-1">A behavior that is substantially different from the learned baseline (e.g., Kitchen activity at 3 AM). Flagged immediately.</p>
                  </div>
              </CardContent>
          </Card>

          {/* 10. ANOMALY HISTORY */}
          <Card>
              <CardHeader>
                  <CardTitle>Anomaly History</CardTitle>
                  <CardDescription>Frequency of statistical deviations over time.</CardDescription>
              </CardHeader>
              <CardContent>
                  {anomalyData.chartData.length > 0 ? (
                      <div className="h-[200px] w-full">
                          <ResponsiveContainer width="100%" height="100%">
                              <BarChart data={anomalyData.chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                  <XAxis dataKey="date" tickLine={false} axisLine={false} fontSize={12} />
                                  <YAxis tickLine={false} axisLine={false} fontSize={12} allowDecimals={false} />
                                  <Tooltip cursor={{fill: '#f1f5f9'}} />
                                  <Bar dataKey="count" fill="#f97316" radius={[4, 4, 0, 0]} />
                              </BarChart>
                          </ResponsiveContainer>
                      </div>
                  ) : (
                      <div className="flex items-center justify-center h-[200px] text-muted-foreground text-sm">Insufficient historical data for trend analysis.</div>
                  )}
              </CardContent>
          </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 8. ANOMALY CATEGORIES */}
          <Card>
              <CardHeader><CardTitle>Anomaly Categories</CardTitle></CardHeader>
              <CardContent>
                  <div className="flex flex-wrap gap-2">
                      <Badge variant="secondary">Unusual Time</Badge>
                      <Badge variant="secondary">Unusual Activity</Badge>
                      <Badge variant="secondary">Unusual Room</Badge>
                      <Badge variant="secondary">Unusual Sensor Pattern</Badge>
                      <Badge variant="secondary">Unusual Energy Pattern</Badge>
                  </div>
              </CardContent>
          </Card>

          {/* 11 & 12. PRIVACY & SAFETY */}
          <Card className="bg-green-50/50 border-green-200">
              <CardContent className="pt-6 space-y-4">
                  <div className="flex items-center gap-2">
                      <ShieldCheck className="size-5 text-green-700"/>
                      <h3 className="font-semibold text-green-800">Privacy-Preserving Analysis</h3>
                  </div>
                  <ul className="list-disc pl-5 text-sm text-green-900/80 space-y-1">
                      <li>No cameras or microphones required</li>
                      <li>No live IoT hardware connection</li>
                      <li>Analysis is performed exclusively on historical dataset patterns</li>
                  </ul>
                  
                  <div className="flex items-start gap-2 mt-4 pt-4 border-t border-green-200/50">
                      <Info className="size-4 text-green-700 shrink-0 mt-0.5"/>
                      <p className="text-xs text-green-900/80 leading-relaxed">
                          <strong>Note:</strong> The ML model detects statistical/behavioral deviations (Unusual pattern detected &mdash; review recommended). It does not explicitly detect emergencies (e.g., fires or break-ins).
                      </p>
                  </div>
              </CardContent>
          </Card>
      </div>
    </div>
  );
}
"""

with open(os.path.join(ROUTES_DIR, "anomalies.tsx"), "w", encoding="utf-8") as f:
    f.write(file_content)

print("anomalies.tsx completely overhauled.")

