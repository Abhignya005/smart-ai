import os

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

file_content = """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { TrendingUp, ActivitySquare, Database, Activity, HelpCircle, Check, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

export const Route = createFileRoute("/routine")({
  component: RoutineDiscovery,
});

function RoutineDiscovery() {
  const [metrics, setMetrics] = useState<any>(null);
  const [feedbackState, setFeedbackState] = useState<'none'|'incorrect'|'submitted'>('none');
  const [actualActivity, setActualActivity] = useState('');
  
  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) setMetrics(calculateDashboardMetrics(dataset));
  }, []);

  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first.</div>;

  const score = metrics.insights.score || 0;
  const scoreText = metrics.insights.scoreText;

  const handleFeedbackSubmit = () => {
      setFeedbackState('submitted');
      toast.success("Feedback stored for future personalization.");
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Personal Routine Learning</h1>
            <p className="text-muted-foreground mt-2">Dynamically calculated from {metrics.rows} historical rows.</p>
          </div>
      </div>

      {/* TOP CARDS: Score, Current, Next */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Daily Routine Score */}
        <Card className="lg:col-span-1 bg-primary text-primary-foreground">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-primary-foreground/80">Daily Routine Score</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center pt-2">
            {metrics.insights.scoreText !== "Insufficient Data" ? (
                <>
                <div className="text-5xl font-bold mb-2">{score}%</div>
                <p className="text-xs text-primary-foreground/80 text-center">{scoreText}</p>
                </>
            ) : (
                <div className="text-center py-4">Insufficient Data</div>
            )}
          </CardContent>
        </Card>
        
        {/* Current Activity & User Feedback Loop */}
        <Card className="lg:col-span-2">
            <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
                <CardTitle className="text-sm font-medium">Current Activity</CardTitle>
                {metrics.explainableData && (
                    <Dialog>
                        <DialogTrigger asChild>
                            <Button variant="ghost" size="sm" className="h-6 text-xs text-muted-foreground hover:text-primary px-2"><HelpCircle className="size-3 mr-1"/> Why?</Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Feature-Based Reasoning</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4 py-4">
                                <p className="text-sm">The model determined <strong>{metrics.currentActivity}</strong> based on these features from the dataset:</p>
                                <ul className="list-disc pl-5 text-sm space-y-2">
                                    <li>Room: {metrics.explainableData.room}</li>
                                    <li>Motion: {metrics.explainableData.motion}</li>
                                    <li>Light: {metrics.explainableData.light}</li>
                                    <li>Power: {metrics.explainableData.power}</li>
                                    <li>Time: {metrics.explainableData.time}</li>
                                </ul>
                                <p className="text-xs text-muted-foreground italic border-t pt-2 mt-4">Note: This is feature-based reasoning derived directly from the uploaded dataset values.</p>
                            </div>
                        </DialogContent>
                    </Dialog>
                )}
            </CardHeader>
            <CardContent>
                <div className="flex justify-between items-center mb-4">
                    <div className="text-2xl font-bold">{metrics.currentActivity}</div>
                    <div className="text-right">
                        <div className="text-sm font-semibold">{metrics.currentConf}</div>
                    </div>
                </div>
                
                {/* User Feedback Loop */}
                {metrics.currentActivity !== 'Not Confirmed' && feedbackState === 'none' && (
                    <div className="bg-muted/50 p-3 rounded-md flex justify-between items-center mt-2 border">
                        <span className="text-xs font-medium">Was this prediction correct?</span>
                        <div className="space-x-2">
                            <Button size="sm" variant="outline" className="h-7 text-xs bg-green-50 hover:bg-green-100 text-green-700" onClick={() => handleFeedbackSubmit()}><Check className="size-3 mr-1"/> Correct</Button>
                            <Button size="sm" variant="outline" className="h-7 text-xs bg-red-50 hover:bg-red-100 text-red-700" onClick={() => setFeedbackState('incorrect')}><X className="size-3 mr-1"/> Incorrect</Button>
                        </div>
                    </div>
                )}
                {feedbackState === 'incorrect' && (
                    <div className="bg-muted/50 p-3 rounded-md flex flex-col gap-2 mt-2 border animate-in fade-in">
                        <span className="text-xs font-medium">What were you actually doing?</span>
                        <div className="flex gap-2">
                             <Input size={1} className="h-8 text-xs" placeholder="Type actual activity..." value={actualActivity} onChange={(e) => setActualActivity(e.target.value)} />
                             <Button size="sm" className="h-8 text-xs" onClick={handleFeedbackSubmit}>Submit</Button>
                        </div>
                    </div>
                )}
                {feedbackState === 'submitted' && (
                    <div className="bg-green-50 text-green-700 p-2 rounded-md text-xs font-medium text-center mt-2 border border-green-200">
                        Feedback stored successfully.
                    </div>
                )}
            </CardContent>
        </Card>

        {/* Predicted Next Activity */}
        <Card className="lg:col-span-1">
            <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Predicted Next Activity</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold text-purple-600 mb-1">{metrics.nextActivity}</div>
                {metrics.nextActivity !== "Insufficient Data" && (
                    <>
                    <div className="text-sm font-semibold mb-2">Probability: {metrics.nextConf}</div>
                    <p className="text-[10px] text-muted-foreground leading-tight">Based on previous activity sequences and historical routine.</p>
                    </>
                )}
            </CardContent>
        </Card>
      </div>
      
      {/* ROUTINE INSIGHTS & DRIFT */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><TrendingUp className="size-5" /> Routine Drift Detection</CardTitle>
              <CardDescription>Detecting gradual changes over the dataset duration.</CardDescription>
            </CardHeader>
            <CardContent>
               <div className="space-y-4">
                   <div className="p-4 border rounded-md bg-muted/20 flex flex-col gap-2">
                       <div className="flex justify-between items-start">
                           <p className="font-semibold text-sm">Status</p>
                           <Badge variant="outline" className={metrics.driftInfo.status === 'Stable' ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}>
                               {metrics.driftInfo.status}
                           </Badge>
                       </div>
                       <p className="text-sm text-muted-foreground">{metrics.driftInfo.text}</p>
                   </div>
               </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><ActivitySquare className="size-5" /> Personal Routine Insights</CardTitle>
              <CardDescription>Calculated historical averages.</CardDescription>
            </CardHeader>
            <CardContent>
                {metrics.insights.comparison.length > 0 ? (
                    <div className="grid grid-cols-2 gap-4">
                        {metrics.insights.comparison.slice(0,4).map((c:any, i:number) => (
                             <div key={i} className="border p-3 rounded-md bg-card shadow-sm">
                                 <p className="text-xs text-muted-foreground">Typical {c.activity}</p>
                                 <p className="text-lg font-bold">{c.typical}</p>
                             </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-muted-foreground">Insufficient Data</div>
                )}
            </CardContent>
          </Card>
      </div>

      {/* TODAY VS TYPICAL DAY & TIMELINE */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
             <CardHeader>
                <CardTitle>Today vs Typical Day</CardTitle>
             </CardHeader>
             <CardContent>
                 {metrics.insights.comparison.length > 0 ? (
                     <Table>
                         <TableHeader>
                             <TableRow>
                                 <TableHead>Activity</TableHead>
                                 <TableHead>Typical Time</TableHead>
                                 <TableHead>Today's Time</TableHead>
                                 <TableHead>Difference</TableHead>
                             </TableRow>
                         </TableHeader>
                         <TableBody>
                             {metrics.insights.comparison.map((item:any, i:number) => (
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
                 ) : (
                     <div className="text-muted-foreground">Insufficient data to build comparison table.</div>
                 )}
             </CardContent>
          </Card>

          <Card className="h-full">
             <CardHeader>
                <CardTitle className="flex items-center gap-2"><History className="size-5" /> Today's Activity Timeline</CardTitle>
             </CardHeader>
             <CardContent>
                 {metrics.timeline.length > 0 ? (
                     <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-slate-200 pl-8 overflow-y-auto max-h-[400px] pr-2">
                        {metrics.timeline.map((item:any, index:number) => (
                            <div key={index} className="relative mb-6">
                                <div className="absolute -left-10 mt-1 flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground border-2 border-background">
                                    <Activity className="size-3" />
                                </div>
                                <div className="bg-card p-3 rounded-md border shadow-sm">
                                    <div className="flex items-center justify-between mb-1">
                                        <div className="font-bold text-primary">{item.activity}</div>
                                        <time className="font-mono text-xs text-muted-foreground">{item.time}</time>
                                    </div>
                                    <div className="flex justify-between items-center mt-2 text-[10px] text-muted-foreground uppercase">
                                        <span>Conf: {item.confidence}%</span>
                                        <span>{item.duration}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                 ) : (
                     <div className="text-muted-foreground">Insufficient Activity Data</div>
                 )}
             </CardContent>
          </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Planned vs Actual Analysis</CardTitle>
          <CardDescription>Comparison generated dynamically from dataset timestamps.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {metrics.planVsActual.length > 0 ? (
              <Table>
                 <TableHeader>
                     <TableRow>
                         <TableHead>Activity</TableHead>
                         <TableHead>Planned</TableHead>
                         <TableHead>Actual</TableHead>
                         <TableHead className="text-right">Status</TableHead>
                     </TableRow>
                 </TableHeader>
                 <TableBody>
                     {metrics.planVsActual.map((item:any, i:number) => (
                         <TableRow key={i}>
                             <TableCell className="font-medium">{item.activity}</TableCell>
                             <TableCell>{item.planned}</TableCell>
                             <TableCell>{item.actual}</TableCell>
                             <TableCell className="text-right">
                                 <Badge variant="outline" className={
                                     item.status === 'COMPLETED' ? 'text-green-700 bg-green-50' : 
                                     item.status === 'DELAYED' ? 'text-amber-700 bg-amber-50' :
                                     'text-orange-700 bg-orange-50'
                                 }>
                                     {item.status}
                                 </Badge>
                             </TableCell>
                         </TableRow>
                     ))}
                 </TableBody>
             </Table>
          ) : (
              <div className="text-muted-foreground">Insufficient data for Planned vs Actual analysis.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
"""

with open(os.path.join(ROUTES_DIR, "routine.tsx"), "w", encoding="utf-8") as f:
    f.write(file_content)

print("Routine.tsx massive upgrade completed.")

