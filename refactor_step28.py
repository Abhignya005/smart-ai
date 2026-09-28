import os

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
LIB_DIR = os.path.join(BASE_DIR, "src", "lib")
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

mlutils_content = """export function calculateDashboardMetrics(dataset: any) {
    if (!dataset || !dataset.data || dataset.data.length === 0) return null;
    
    const headers = dataset.headers.map((h: string) => h.toLowerCase());
    
    // Find key columns dynamically
    const powerCol = dataset.headers.find((h: string) => h.toLowerCase().includes('power') || h.toLowerCase().includes('energy') || h.toLowerCase().includes('kw'));
    const activityCol = dataset.headers.find((h: string) => h.toLowerCase().includes('activity'));
    const timeCol = dataset.headers.find((h: string) => h.toLowerCase().includes('time') || h.toLowerCase().includes('date'));
    const roomCol = dataset.headers.find((h: string) => h.toLowerCase().includes('room'));
    
    // Chronologically sort data based on timestamp if available
    let data = [...dataset.data];
    if (timeCol) {
        data.sort((a, b) => {
            const dateA = new Date(a[timeCol]).getTime();
            const dateB = new Date(b[timeCol]).getTime();
            return (isNaN(dateA) ? 0 : dateA) - (isNaN(dateB) ? 0 : dateB);
        });
    }
    
    const parseTimeToMinutes = (timeStr: string) => {
        if (!timeStr) return -1;
        const parts = timeStr.split(' ');
        const t = parts.length > 1 ? parts[1] : parts[0];
        if (!t.includes(':')) return -1;
        const [h, m] = t.split(':').map(Number);
        if (isNaN(h) || isNaN(m)) return -1;
        return h * 60 + m;
    };
    
    const formatMinutesToTime = (mins: number) => {
        if (isNaN(mins) || mins < 0) return "--:--";
        let norm = Math.round(mins) % 1440;
        if (norm < 0) norm += 1440;
        const h = Math.floor(norm / 60);
        const m = Math.floor(norm % 60);
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
    };

    const calculateTypicalTime = (minutesArr: number[]) => {
        if (minutesArr.length === 0) return NaN;
        if (minutesArr.length <= 2) {
            let sumSin = 0, sumCos = 0;
            minutesArr.forEach(m => {
                const angle = (m / 1440) * 2 * Math.PI;
                sumSin += Math.sin(angle);
                sumCos += Math.cos(angle);
            });
            let avgAngle = Math.atan2(sumSin / minutesArr.length, sumCos / minutesArr.length);
            if (avgAngle < 0) avgAngle += 2 * Math.PI;
            return (avgAngle / (2 * Math.PI)) * 1440;
        }

        let maxDensity = 0;
        let bestCenter = 0;
        for (let center = 0; center < 1440; center += 15) {
            let count = 0;
            let sumSin = 0;
            let sumCos = 0;
            minutesArr.forEach(m => {
                let diff = Math.abs(m - center);
                if (diff > 720) diff = 1440 - diff;
                if (diff <= 45) {
                    count++;
                    const angle = (m / 1440) * 2 * Math.PI;
                    sumSin += Math.sin(angle);
                    sumCos += Math.cos(angle);
                }
            });
            if (count > maxDensity) {
                maxDensity = count;
                let avgAngle = Math.atan2(sumSin / count, sumCos / count);
                if (avgAngle < 0) avgAngle += 2 * Math.PI;
                bestCenter = (avgAngle / (2 * Math.PI)) * 1440;
            }
        }
        return maxDensity > 0 ? bestCenter : NaN;
    };

    let rows = data.length.toLocaleString();
    let rawRowCount = data.length;
    let cols = dataset.headers.length;

    let timeline: any[] = [];
    let availableDates = new Set<string>();
    
    if (activityCol && timeCol) {
        data.forEach((r: any) => {
            const rawTime = r[timeCol];
            if (rawTime && r[activityCol]) {
                const datePart = rawTime.includes(' ') ? rawTime.split(' ')[0] : 'Historical';
                const timePart = rawTime.includes(' ') ? rawTime.split(' ')[1] : rawTime;
                availableDates.add(datePart);
                timeline.push({
                    date: datePart,
                    time: timePart,
                    activity: r[activityCol],
                    confidence: 100, // Explicit historical labels are 100% true
                    duration: "Recorded",
                    rawMins: parseTimeToMinutes(rawTime)
                });
            }
        });
    }

    let currentActivity = 'Not Confirmed';
    let currentConf = 'Insufficient Data';
    let nextActivity = 'Insufficient Data';
    let nextConf = 'Insufficient Data';
    let lastTimestamp = '--:--';

    if (timeline.length > 0) {
        const last = timeline[timeline.length - 1];
        currentActivity = last.activity;
        currentConf = `Observed Label`;
        lastTimestamp = last.time;
        
        if (timeline.length > 5) {
             let nextMap: any = {};
             for(let i=0; i<timeline.length-1; i++){
                 if (timeline[i].activity === currentActivity) {
                     const next = timeline[i+1].activity;
                     nextMap[next] = (nextMap[next] || 0) + 1;
                 }
             }
             let bestNext = '';
             let bestCount = 0;
             let total = 0;
             for (const [k, v] of Object.entries(nextMap)) {
                 total += v as number;
                 if ((v as number) > bestCount) {
                     bestCount = v as number;
                     bestNext = k;
                 }
             }
             
             if (bestNext && total > 0) {
                 nextActivity = bestNext;
                 const prob = Math.round((bestCount / total) * 100);
                 nextConf = `${prob}%`;
                 if (prob < 30) nextActivity = 'Low Confidence';
             }
        }
    }

    let consistency = 'Insufficient Data';
    let planVsActual: any[] = [];
    let insights = { comparison: [] as any[] };
    let driftInfo = { status: 'Insufficient Data', text: 'Requires more historical data for drift analysis.' };
    
    if (activityCol && timeCol && data.length > 10) {
        const splitIdx = Math.max(0, data.length - 15);
        const historyData = data.slice(0, splitIdx);
        const todayData = data.slice(splitIdx);
        
        let histTypicalRaw: any = {};
        historyData.forEach((r:any) => {
            const act = r[activityCol];
            const mins = parseTimeToMinutes(r[timeCol]);
            if (act && mins >= 0) {
                if (!histTypicalRaw[act]) histTypicalRaw[act] = [];
                histTypicalRaw[act].push(mins);
            }
        });

        let histTypical: any = {};
        Object.keys(histTypicalRaw).forEach(k => {
            const arr = histTypicalRaw[k];
            if(arr.length > 0) {
                histTypical[k] = calculateTypicalTime(arr);
            }
        });

        let matchCount = 0;
        let totalCount = 0;
        let comparisonList: any[] = [];

        todayData.forEach((r:any) => {
            const act = r[activityCol];
            const mins = parseTimeToMinutes(r[timeCol]);
            if (act && histTypical[act] !== undefined && !isNaN(histTypical[act]) && mins >= 0) {
                totalCount++;
                let diff = Math.abs(mins - histTypical[act]);
                if (diff > 720) diff = 1440 - diff;
                
                if (diff < 60) matchCount++; 
                
                const timeStr = r[timeCol].includes(' ') ? r[timeCol].split(' ')[1] : r[timeCol];
                
                let stat = 'On Time';
                let rawDiff = mins - histTypical[act];
                if (rawDiff > 720) rawDiff -= 1440;
                if (rawDiff < -720) rawDiff += 1440;
                
                if (rawDiff > 60) stat = 'Late';
                if (rawDiff < -60) stat = 'Early';

                comparisonList.push({
                    activity: act,
                    typical: formatMinutesToTime(histTypical[act]),
                    today: timeStr,
                    diffMins: Math.round(rawDiff),
                    status: stat
                });
                
                planVsActual.push({
                    activity: act,
                    planned: formatMinutesToTime(histTypical[act]),
                    actual: timeStr,
                    status: stat === 'On Time' ? 'COMPLETED' : stat === 'Late' ? 'DELAYED' : 'COMPLETED'
                });
            }
        });
        
        if (totalCount > 0) {
            consistency = `${Math.round((matchCount / totalCount) * 100)}%`;
        }
        
        if (historyData.length > 20) {
            const h1 = historyData.slice(0, Math.floor(historyData.length/2));
            const h2 = historyData.slice(Math.floor(historyData.length/2));
            
            const actFreq: any = {};
            h1.forEach((r:any) => actFreq[r[activityCol]] = (actFreq[r[activityCol]]||0)+1);
            const topAct = Object.keys(actFreq).sort((a,b)=>actFreq[b]-actFreq[a])[0];
            
            if (topAct) {
                let h1Mins = h1.filter((r:any)=>r[activityCol]===topAct).map((r:any)=>parseTimeToMinutes(r[timeCol]));
                let h2Mins = h2.filter((r:any)=>r[activityCol]===topAct).map((r:any)=>parseTimeToMinutes(r[timeCol]));
                
                if (h1Mins.length > 2 && h2Mins.length > 2) {
                    const t1 = calculateTypicalTime(h1Mins);
                    const t2 = calculateTypicalTime(h2Mins);
                    if (!isNaN(t1) && !isNaN(t2)) {
                        let driftDiff = t2 - t1;
                        if (driftDiff > 720) driftDiff -= 1440;
                        if (driftDiff < -720) driftDiff += 1440;
                        
                        if (Math.abs(driftDiff) > 45) {
                            driftInfo.status = 'Drift Detected';
                            const dir = driftDiff > 0 ? 'later' : 'earlier';
                            driftInfo.text = `Your ${topAct} routine shifted ${Math.round(Math.abs(driftDiff))} minutes ${dir}.`;
                        } else {
                            driftInfo.status = 'Stable';
                            driftInfo.text = 'No significant routine drift detected.';
                        }
                    }
                }
            }
        }

        insights.comparison = Object.keys(histTypical).map(k => ({
            activity: k,
            typical: formatMinutesToTime(histTypical[k]),
            today: '--:--',
            diffMins: 0,
            status: 'Baseline'
        }));
        
        comparisonList.forEach(c => {
             const exist = insights.comparison.find(i => i.activity === c.activity);
             if (exist) {
                 exist.today = c.today;
                 exist.diffMins = c.diffMins;
                 exist.status = c.status;
             }
        });
        
        insights.comparison = insights.comparison.sort((a,b) => parseTimeToMinutes(a.typical) - parseTimeToMinutes(b.typical));
        planVsActual = planVsActual.reverse().slice(0, 5);
    }
    
    let anomalies = 'Insufficient Data';
    if (activityCol && timeCol && data.length > 5) {
        let anomalyCount = 0;
        data.forEach((r:any) => {
             const act = r[activityCol];
             const mins = parseTimeToMinutes(r[timeCol]);
             if (act && mins >= 0 && insights.comparison.length > 0) {
                 const typicalEntry = insights.comparison.find((x:any) => x.activity === act);
                 if (typicalEntry) {
                     const typMins = parseTimeToMinutes(typicalEntry.typical);
                     let diff = Math.abs(mins - typMins);
                     if (diff > 720) diff = 1440 - diff;
                     if (diff > 180) anomalyCount++;
                 }
             }
             if (powerCol) {
                 const p = parseFloat(r[powerCol]);
                 if (!isNaN(p) && p > 4.5) anomalyCount++;
             }
        });
        anomalies = anomalyCount.toString();
    }

    let peakEnergy = 'Not Available';
    let forecast = 'Insufficient Data';
    if (powerCol) {
        let max = -Infinity;
        let sum = 0;
        let count = 0;
        let hourlyData: any = {};
        
        data.forEach((r: any) => {
            const p = parseFloat(r[powerCol]);
            if (!isNaN(p)) {
                if (p > max) max = p;
                sum += p;
                count++;
                if (timeCol) {
                    const mins = parseTimeToMinutes(r[timeCol]);
                    if (mins >= 0) {
                        const h = Math.floor(mins / 60);
                        if (!hourlyData[h]) hourlyData[h] = [];
                        hourlyData[h].push(p);
                    }
                }
            }
        });
        if (max > -Infinity) peakEnergy = `${max.toFixed(2)} kW`;
        if (count > 5 && timeCol && timeline.length > 0) {
            const lastTime = timeline[timeline.length - 1].rawMins;
            const currHour = Math.floor(lastTime / 60);
            const nextHour = (currHour + 1) % 24;
            if (hourlyData[nextHour] && hourlyData[nextHour].length > 0) {
                const arr = hourlyData[nextHour];
                const avg = arr.reduce((a:number,b:number)=>a+b,0) / arr.length;
                forecast = `Predicted ${(avg).toFixed(2)} kW for upcoming hour`;
            } else {
                forecast = `Predicted ${(sum/count).toFixed(2)} kW (Daily Average)`;
            }
        }
    }

    return {
        isEmpty: false,
        rows,
        rawRowCount,
        cols,
        consistency,
        anomalies,
        peakEnergy,
        forecast,
        currentActivity,
        currentConf,
        nextActivity,
        nextConf,
        lastTimestamp,
        timeline, // Kept chronological order
        availableDates: Array.from(availableDates).sort(),
        planVsActual,
        insights,
        driftInfo
    };
}
"""

routine_content = """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { TrendingUp, Activity, ActivitySquare, ShieldAlert, History, Database } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useState, useEffect } from "react";

export const Route = createFileRoute("/routine")({
  component: RoutineDiscovery,
});

function RoutineDiscovery() {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) {
          setMetrics(calculateDashboardMetrics(dataset));
      }
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
"""

with open(os.path.join(LIB_DIR, "mlUtils.ts"), "w", encoding="utf-8") as f:
    f.write(mlutils_content)

with open(os.path.join(ROUTES_DIR, "routine.tsx"), "w", encoding="utf-8") as f:
    f.write(routine_content)

print("Updated routine.tsx and mlUtils.ts for absolute dataset strictness.")

