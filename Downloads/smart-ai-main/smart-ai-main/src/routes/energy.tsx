import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Database, Zap, Activity, Info, MapPin, Clock, Calendar } from "lucide-react";
import { loadDataset, getOrFetchDataset, onDatasetUpdate } from "@/lib/datasetUtils";
import { useState, useEffect, useMemo } from "react";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/energy")({
  component: EnergyIntelligence,
});

function EnergyIntelligence() {
  const [dataset, setDataset] = useState<any>(null);

  const loadData = () => {
    getOrFetchDataset().then((d) => {
      if (d) setDataset(d);
    });
  };

  useEffect(() => {
    loadData();
    const unsubscribe = onDatasetUpdate((updatedDs) => {
      if (updatedDs) setDataset(updatedDs);
      else loadData();
    });
    return unsubscribe;
  }, []);

  const energyData = useMemo(() => {
      if (!dataset || dataset.data.length === 0) return null;
      
      const data = dataset.data;
      const h = dataset.headers.map((hd: string) => hd.toLowerCase());
      
      const timeCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('time') || hd.toLowerCase().includes('date'));
      const actCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('activity'));
      const roomCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('room'));
      const powerCol = dataset.headers.find((hd: string) => hd.toLowerCase().includes('power') || hd.toLowerCase().includes('kw') || hd.toLowerCase().includes('energy'));

      if (!powerCol) return { noPower: true, headers: dataset.headers };

      let max = -Infinity;
      let min = Infinity;
      let sum = 0;
      let count = 0;
      let maxEvent = null;
      
      let timeline: any[] = [];
      let roomStats: any = {};
      let actStats: any = {};

      data.forEach((r:any) => {
          const p = parseFloat(r[powerCol]);
          if (!isNaN(p)) {
              if (p > max) {
                  max = p;
                  maxEvent = r;
              }
              if (p < min) min = p;
              sum += p;
              count++;
              
              const t = timeCol ? r[timeCol] : '';
              timeline.push({ time: t, power: p });
              
              if (roomCol && r[roomCol]) {
                  if (!roomStats[r[roomCol]]) roomStats[r[roomCol]] = [];
                  roomStats[r[roomCol]].push(p);
              }
              
              if (actCol && r[actCol]) {
                  if (!actStats[r[actCol]]) actStats[r[actCol]] = [];
                  actStats[r[actCol]].push(p);
              }
          }
      });

      if (count === 0) return { noPowerData: true };
      
      const avg = sum / count;
      
      const calcAverages = (statsObj: any) => {
          return Object.keys(statsObj).map(k => {
              const arr = statsObj[k];
              const avgVal = arr.reduce((a:number,b:number)=>a+b,0) / arr.length;
              return { name: k, value: parseFloat(avgVal.toFixed(2)) };
          }).sort((a,b) => b.value - a.value);
      };

      const period = timeCol && data.length > 0 ? `${data[0][timeCol]} to ${data[data.length-1][timeCol]}` : 'Unknown';

      return {
          records: data.length,
          timeCol, actCol, roomCol, powerCol,
          peak: max.toFixed(2),
          min: min.toFixed(2),
          avg: avg.toFixed(2),
          period,
          timeline,
          maxEvent,
          roomChart: calcAverages(roomStats),
          actChart: calcAverages(actStats)
      };
  }, [dataset]);

  if (!dataset) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>No dataset available. Upload a dataset to analyze energy intelligence.</div>;
  if (energyData?.noPower || energyData?.noPowerData) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Insufficient data: No valid power/energy column found in the uploaded dataset.</div>;
  if (!energyData) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Insufficient data for reliable energy analysis.</div>;

  return (
    <div className="space-y-6 h-full pb-10">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Energy Intelligence</h1>
        <p className="text-muted-foreground mt-2">Privacy-Preserving Personal Routine & Activity Intelligence.</p>
      </div>

      {/* 1. DATA AVAILABILITY & PRIVACY */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="bg-slate-50">
              <CardContent className="pt-6">
                  <h3 className="font-semibold text-sm mb-3">Data Availability (Mapped Columns)</h3>
                  <div className="flex flex-wrap gap-2">
                      <Badge variant="outline">{energyData.powerCol} &rarr; Power</Badge>
                      {energyData.timeCol && <Badge variant="outline">{energyData.timeCol} &rarr; Time</Badge>}
                      {energyData.roomCol && <Badge variant="outline">{energyData.roomCol} &rarr; Room</Badge>}
                      {energyData.actCol && <Badge variant="outline">{energyData.actCol} &rarr; Activity</Badge>}
                  </div>
              </CardContent>
          </Card>
          <Card className="bg-blue-50/50 border-blue-200">
              <CardContent className="pt-6">
                  <h3 className="font-semibold text-sm text-blue-800 mb-2">Privacy-Preserving Historical Analysis</h3>
                  <p className="text-xs text-blue-900/80">This page analyzes historical dataset values. There is NO IoT hardware, live sensor integration, or active smart plug monitoring. Energy data is used strictly to support behavioral and routine intelligence.</p>
              </CardContent>
          </Card>
      </div>

      {/* 2. ENERGY SUMMARY */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-xs font-medium text-muted-foreground">Records Analyzed</CardTitle></CardHeader><CardContent><div className="text-xl font-bold">{energyData.records}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-xs font-medium text-muted-foreground">Peak Power</CardTitle></CardHeader><CardContent><div className="text-xl font-bold text-red-500">{energyData.peak} kW</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-xs font-medium text-muted-foreground">Average Power</CardTitle></CardHeader><CardContent><div className="text-xl font-bold text-blue-500">{energyData.avg} kW</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-xs font-medium text-muted-foreground">Minimum Power</CardTitle></CardHeader><CardContent><div className="text-xl font-bold text-green-500">{energyData.min} kW</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-xs font-medium text-muted-foreground">Analysis Period</CardTitle></CardHeader><CardContent><div className="text-xs font-bold truncate mt-1" title={energyData.period}>{energyData.period}</div></CardContent></Card>
      </div>

      {/* 3. HIGHEST CONSUMPTION EVENT */}
      {energyData.maxEvent && (
          <Card className="border-red-100 bg-red-50/30">
              <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-red-800"><Zap className="size-5"/> Highest Consumption Event</CardTitle>
                  <CardDescription>The single highest energy spike recorded in the dataset.</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-6">
                  <div className="space-y-1">
                      <p className="text-xs text-muted-foreground uppercase font-semibold">Power</p>
                      <p className="font-bold text-lg text-red-700">{energyData.peak} kW</p>
                  </div>
                  {energyData.timeCol && (
                      <div className="space-y-1">
                          <p className="text-xs text-muted-foreground uppercase font-semibold">Timestamp</p>
                          <p className="font-medium flex items-center gap-1"><Clock className="size-3"/> {energyData.maxEvent[energyData.timeCol]}</p>
                      </div>
                  )}
                  {energyData.roomCol && (
                      <div className="space-y-1">
                          <p className="text-xs text-muted-foreground uppercase font-semibold">Room</p>
                          <p className="font-medium flex items-center gap-1"><MapPin className="size-3"/> {energyData.maxEvent[energyData.roomCol]}</p>
                      </div>
                  )}
                  {energyData.actCol && (
                      <div className="space-y-1">
                          <p className="text-xs text-muted-foreground uppercase font-semibold">Activity</p>
                          <p className="font-medium flex items-center gap-1"><Activity className="size-3"/> {energyData.maxEvent[energyData.actCol]}</p>
                      </div>
                  )}
              </CardContent>
          </Card>
      )}

      {/* 4. ENERGY TIMELINE */}
      {energyData.timeCol ? (
          <Card>
              <CardHeader>
                  <CardTitle>Energy Timeline</CardTitle>
                  <CardDescription>Chronological power usage across the uploaded dataset.</CardDescription>
              </CardHeader>
              <CardContent>
                  <div className="h-[250px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={energyData.timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                              <defs>
                                  <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1">
                                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                                  </linearGradient>
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
      ) : (
          <Card><CardContent className="p-6 text-center text-muted-foreground">Insufficient data: Missing time/timestamp column for Energy Timeline.</CardContent></Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 5. ENERGY BY ROOM */}
          <Card>
              <CardHeader>
                  <CardTitle>Average Energy by Room</CardTitle>
              </CardHeader>
              <CardContent>
                  {energyData.roomCol ? (
                      energyData.roomChart.length > 0 ? (
                          <div className="h-[200px] w-full">
                              <ResponsiveContainer width="100%" height="100%">
                                  <BarChart data={energyData.roomChart} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                      <XAxis type="number" fontSize={12} />
                                      <YAxis dataKey="name" type="category" fontSize={12} tickLine={false} axisLine={false} />
                                      <Tooltip cursor={{fill: '#f1f5f9'}} />
                                      <Bar dataKey="value" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                                  </BarChart>
                              </ResponsiveContainer>
                          </div>
                      ) : (
                           <div className="flex items-center justify-center h-[200px] text-muted-foreground text-sm">No valid room data points.</div>
                      )
                  ) : (
                      <div className="flex flex-col items-center justify-center h-[200px] text-muted-foreground text-sm space-y-2">
                          <MapPin className="size-8 opacity-20"/>
                          <p>Insufficient data: Room column is required.</p>
                      </div>
                  )}
              </CardContent>
          </Card>

          {/* 6. ENERGY BY ACTIVITY */}
          <Card>
              <CardHeader>
                  <CardTitle>Average Energy by Activity</CardTitle>
              </CardHeader>
              <CardContent>
                  {energyData.actCol ? (
                      energyData.actChart.length > 0 ? (
                          <div className="h-[200px] w-full">
                              <ResponsiveContainer width="100%" height="100%">
                                  <BarChart data={energyData.actChart} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                      <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={12} />
                                      <YAxis tickLine={false} axisLine={false} fontSize={12} />
                                      <Tooltip cursor={{fill: '#f1f5f9'}} />
                                      <Bar dataKey="value" fill="#ec4899" radius={[4, 4, 0, 0]} />
                                  </BarChart>
                              </ResponsiveContainer>
                          </div>
                      ) : (
                          <div className="flex items-center justify-center h-[200px] text-muted-foreground text-sm">No valid activity data points.</div>
                      )
                  ) : (
                      <div className="flex flex-col items-center justify-center h-[200px] text-muted-foreground text-sm space-y-2">
                          <Activity className="size-8 opacity-20"/>
                          <p>Insufficient data: Activity column is required.</p>
                      </div>
                  )}
              </CardContent>
          </Card>
      </div>

      {/* 7. PEAK VS AVERAGE & INSIGHT CONNECTION */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
              <CardHeader><CardTitle>Peak vs Average Comparison</CardTitle></CardHeader>
              <CardContent className="space-y-6 pt-4">
                  <div className="space-y-2">
                      <div className="flex justify-between text-sm font-medium">
                          <span>Average Sustained Usage</span>
                          <span className="text-blue-600">{energyData.avg} kW</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-3">
                          <div className="bg-blue-500 h-3 rounded-full" style={{ width: `${Math.min((parseFloat(energyData.avg)/parseFloat(energyData.peak))*100, 100)}%` }}></div>
                      </div>
                  </div>
                  <div className="space-y-2">
                      <div className="flex justify-between text-sm font-medium">
                          <span>Maximum Spike (Peak)</span>
                          <span className="text-red-600">{energyData.peak} kW</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-3">
                          <div className="bg-red-500 h-3 rounded-full" style={{ width: '100%' }}></div>
                      </div>
                  </div>
              </CardContent>
          </Card>

          {energyData.actCol && energyData.powerCol && (
             <Card className="bg-amber-50/50 border-amber-200">
                 <CardHeader><CardTitle className="text-amber-800 flex items-center gap-2"><Info className="size-5"/> ML Routine Insight Connection</CardTitle></CardHeader>
                 <CardContent>
                     <p className="text-sm text-amber-900/80 leading-relaxed">
                         In a privacy-preserving system, power consumption patterns are heavily utilized as mathematical features to verify activities. 
                         For example, higher energy spikes often provide the statistical confidence needed by the ML model to differentiate an active state (like Cooking or Watching TV) from an inactive state (like Sleep), without relying on cameras.
                     </p>
                 </CardContent>
             </Card>
          )}
      </div>

    </div>
  );
}
