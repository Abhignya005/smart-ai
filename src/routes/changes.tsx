import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ShieldAlert, TrendingUp, ActivitySquare } from "lucide-react";

export const Route = createFileRoute("/changes")({ component: ChangesView });

function ChangesView() {
  return (
    <div className="space-y-10 pb-16 animate-in fade-in duration-500">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Routine Changes</h1>
        <p className="text-muted-foreground text-lg mt-2">Differentiating between normal deviations, gradual drift, and statistical anomalies.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
             <CardHeader>
                 <CardTitle className="flex items-center gap-2 text-slate-800"><ActivitySquare className="size-5 text-blue-500"/> Normal Deviation</CardTitle>
                 <CardDescription>Minor, expected variations in daily schedule.</CardDescription>
             </CardHeader>
             <CardContent className="pt-4 border-t border-slate-100 mt-2">
                 <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                     <p className="text-sm font-medium text-slate-700">"Breakfast was 15 minutes later than usual."</p>
                 </div>
                 <p className="text-xs text-slate-500 mt-4 leading-relaxed">The model expects these natural variations and does not flag them as problematic.</p>
             </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
             <CardHeader>
                 <CardTitle className="flex items-center gap-2 text-slate-800"><TrendingUp className="size-5 text-amber-500"/> Routine Drift</CardTitle>
                 <CardDescription>Gradual, sustained changes over time.</CardDescription>
             </CardHeader>
             <CardContent className="pt-4 border-t border-slate-100 mt-2">
                 <div className="bg-amber-50/50 p-4 rounded-lg border border-amber-200">
                     <p className="text-sm font-medium text-amber-900">"Your average sleep time shifted 32 minutes later over the last 3 weeks."</p>
                 </div>
                 <p className="text-xs text-slate-500 mt-4 leading-relaxed">The ML baseline automatically adapts to drift without generating false alarms.</p>
             </CardContent>
          </Card>

          <Card className="border-red-200 shadow-sm hover:shadow-md transition-all bg-red-50/20">
             <CardHeader>
                 <CardTitle className="flex items-center gap-2 text-red-800"><ShieldAlert className="size-5 text-red-500"/> Anomaly</CardTitle>
                 <CardDescription>Sudden, statistically significant deviations.</CardDescription>
             </CardHeader>
             <CardContent className="pt-4 border-t border-red-100 mt-2">
                 <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                     <p className="text-sm font-medium text-red-900">"Activity at 3:12 AM differs significantly from the learned baseline."</p>
                 </div>
                 <p className="text-xs text-slate-500 mt-4 leading-relaxed">Requires immediate review. Flagged by the Isolation Forest model.</p>
             </CardContent>
          </Card>
      </div>
      
      <div className="mt-8 text-center p-6 bg-slate-50 rounded-xl border border-slate-200">
          <p className="text-slate-600">For a detailed list of detected anomalies, please visit the <a href="/anomalies" className="text-primary font-bold hover:underline">Anomaly Detection</a> engine.</p>
      </div>
    </div>
  );
}
