import os

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

file_content = """import { createFileRoute } from '@tanstack/react-router'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Database, Activity, History, Zap, ShieldAlert, BarChart3, TrendingUp, AlertTriangle } from "lucide-react"
import { loadDataset } from "@/lib/datasetUtils"
import { calculateDashboardMetrics } from "@/lib/mlUtils"
import { useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Link } from "@tanstack/react-router"

export const Route = createFileRoute('/')({
  component: Index,
})

function Index() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) {
          const calculated = calculateDashboardMetrics(dataset);
          setMetrics(calculated);
      }
      setLoading(false);
  }, []);

  if (loading) return null;

  // Fallback empty metrics if no dataset uploaded
  const m = metrics || {
      rows: 0,
      consistency: "Awaiting Data",
      anomalies: "Awaiting Data",
      peakEnergy: "Awaiting Data",
      forecast: "Upload dataset to begin.",
      currentActivity: "Awaiting Data",
      currentConf: "",
      nextActivity: "Awaiting Data",
      nextConf: "",
      timeline: [],
      planVsActual: [],
      lastTimestamp: "N/A",
      isEmpty: true
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">SmartHome Analytics Dashboard</h1>
          <p className="text-muted-foreground mt-2">Privacy-Preserving Machine Learning for Household Intelligence.</p>
        </div>
        {m.isEmpty && (
           <Button asChild variant="default" className="animate-pulse">
               <Link to="/ingestion">Upload Dataset to Start</Link>
           </Button>
        )}
      </div>

      {/* TOP METRICS ROW */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className={m.isEmpty ? "opacity-60 bg-muted/20" : ""}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Dataset Status</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{m.rows.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Rows analyzed</p>
          </CardContent>
        </Card>
        
        <Card className={m.isEmpty ? "opacity-60 bg-muted/20" : ""}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Routine Consistency</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
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
                <p className="text-xs text-muted-foreground">No power feature found in dataset.</p> :
                <p className="text-xs text-muted-foreground">{m.forecast}</p>
            }
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* CURRENT & NEXT ACTIVITY */}
          <div className="space-y-6">
              <Card className={m.isEmpty ? "opacity-60 bg-muted/20" : ""}>
                  <CardHeader>
                      <CardTitle className="flex items-center gap-2"><Activity className="size-5" /> Current Activity</CardTitle>
                  </CardHeader>
                  <CardContent>
                      <div className="flex justify-between items-center">
                          <div>
                              <h2 className={`text-3xl font-bold ${m.isEmpty ? 'text-muted-foreground text-xl' : 'text-primary'}`}>{m.currentActivity}</h2>
                              <p className="text-sm text-muted-foreground">Detected at: {m.lastTimestamp}</p>
                          </div>
                          {m.currentActivity !== 'Not Confirmed' && !m.isEmpty && (
                              <div className="text-right">
                                  <p className="text-sm font-semibold">Confidence</p>
                                  <p className="text-xl font-bold">{m.currentConf}</p>
                              </div>
                          )}
                      </div>
                  </CardContent>
              </Card>
              
              <Card className={m.isEmpty ? "opacity-60 bg-muted/20" : ""}>
                  <CardHeader>
                      <CardTitle className="flex items-center gap-2"><TrendingUp className="size-5" /> Next Activity Prediction</CardTitle>
                  </CardHeader>
                  <CardContent>
                       <div className="flex justify-between items-center">
                          <div>
                              <h2 className={`text-3xl font-bold ${m.isEmpty ? 'text-muted-foreground text-xl' : 'text-purple-600'}`}>{m.nextActivity}</h2>
                          </div>
                          {m.nextActivity !== 'Insufficient Data' && !m.isEmpty && (
                              <div className="text-right">
                                  <p className="text-sm font-semibold">Probability</p>
                                  <p className="text-xl font-bold">{m.nextConf}</p>
                              </div>
                          )}
                      </div>
                  </CardContent>
              </Card>
          </div>

          {/* TIMELINE */}
          <Card className={m.isEmpty ? "opacity-60 bg-muted/20" : ""}>
             <CardHeader>
                <CardTitle className="flex items-center gap-2"><History className="size-5" /> Today's Timeline</CardTitle>
                <CardDescription>Generated from uploaded historical dataset records.</CardDescription>
             </CardHeader>
             <CardContent>
                 {m.timeline.length > 0 ? (
                     <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                        {m.timeline.map((item:any, index:number) => (
                            <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                                <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-slate-300 group-[.is-active]:bg-primary text-slate-500 group-[.is-active]:text-primary-foreground shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                                    <Activity className="size-4" />
                                </div>
                                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-card p-4 rounded border shadow flex justify-between items-center">
                                    <div className="font-bold text-primary">{item.activity}</div>
                                    <time className="font-mono text-xs text-muted-foreground">{item.time}</time>
                                </div>
                            </div>
                        ))}
                    </div>
                 ) : (
                     <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
                         <AlertTriangle className="size-6 mb-2"/>
                         <p>Waiting for Activity Data</p>
                     </div>
                 )}
             </CardContent>
          </Card>
      </div>
      
      {/* PLANNED VS ACTUAL */}
      {!m.isEmpty && m.planVsActual.length > 0 && (
          <Card>
              <CardHeader>
                  <CardTitle>Planned vs Actual Analysis</CardTitle>
                  <CardDescription>Comparison based on uploaded dataset.</CardDescription>
              </CardHeader>
              <CardContent>
                  {m.planVsActual.map((item:any, i:number) => (
                      <div key={i} className="border rounded-md p-4 bg-muted/20 flex flex-col md:flex-row justify-between items-center gap-4">
                        <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                            <p className="text-xs font-medium text-muted-foreground uppercase">Expected Plan</p>
                            <p className="font-bold">{item.expected}</p>
                        </div>
                        <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                            <p className="text-xs font-medium text-muted-foreground uppercase">Observed from Dataset</p>
                            <p className="font-bold">{item.observed}</p>
                        </div>
                        <div className="text-center md:text-right w-full md:w-1/3">
                            <Badge variant="outline" className="text-green-700 bg-green-50 border-green-200">{item.status}</Badge>
                        </div>
                      </div>
                  ))}
              </CardContent>
          </Card>
      )}
    </div>
  );
}
"""

with open(os.path.join(ROUTES_DIR, "index.tsx"), "w", encoding="utf-8") as f:
    f.write(file_content)

print("Empty state fixed.")
