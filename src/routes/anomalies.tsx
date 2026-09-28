import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ShieldAlert, AlertCircle, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/anomalies")({
  component: AnomalyDetection,
});

function AnomalyDetection() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Anomaly & Safety Detection</h1>
          <p className="text-muted-foreground mt-2">Isolation Forest implementation to flag statistically significant deviations.</p>
        </div>
        <Badge variant="outline" className="bg-blue-50 text-blue-700 py-1">Model Ready</Badge>
      </div>

      <Card className="border-orange-200 shadow-sm">
        <CardHeader className="bg-orange-50/50 pb-4">
          <CardTitle className="flex items-center gap-2 text-orange-700">
             <AlertCircle className="size-5" /> Unusual activity detected. Review the event.
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4 space-y-4">
           <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
               <div className="space-y-3">
                   <div>
                       <p className="text-xs text-muted-foreground font-semibold uppercase">Timestamp</p>
                       <p className="font-medium">Today, 3:12 AM</p>
                   </div>
                   <div>
                       <p className="text-xs text-muted-foreground font-semibold uppercase">Sensor Evidence</p>
                       <p className="font-medium">Oven Active (Power Spiked to 2.4 kW)</p>
                   </div>
               </div>
               <div className="space-y-3">
                   <div>
                       <p className="text-xs text-muted-foreground font-semibold uppercase">Expected Behavior</p>
                       <p className="font-medium text-green-700">Oven usage between 6 PM–9 PM (Cooking Routine)</p>
                   </div>
                   <div>
                       <p className="text-xs text-muted-foreground font-semibold uppercase">Observed Behavior</p>
                       <p className="font-medium text-red-600">Oven active at 3:12 AM</p>
                   </div>
               </div>
           </div>
           
           <div className="bg-muted p-4 rounded-md flex justify-between items-center mt-4">
               <div>
                   <p className="font-bold">Anomaly Score: -0.84</p>
                   <p className="text-sm text-muted-foreground">High deviation from clustered behavioral norms.</p>
               </div>
               <div className="space-x-2">
                   <Button variant="outline" size="sm">Dismiss</Button>
                   <Button size="sm" variant="destructive">Flag for Review</Button>
               </div>
           </div>
        </CardContent>
      </Card>
      
      <h3 className="text-lg font-semibold mt-8 mb-2">Historical Log</h3>
      <div className="border rounded-md divide-y">
         <div className="p-4 flex justify-between items-center">
            <div className="flex gap-4 items-center">
                <CheckCircle2 className="text-green-500 size-5" />
                <div><p className="font-medium text-sm">Routine Normalcy</p><p className="text-xs text-muted-foreground">Yesterday, 11:00 PM</p></div>
            </div>
            <Badge variant="outline">Score: 0.92</Badge>
         </div>
      </div>
    </div>
  );
}
