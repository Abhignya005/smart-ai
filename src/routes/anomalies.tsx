import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ShieldAlert, Database } from "lucide-react";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/anomalies")({
  component: AnomalyDetection,
});

function AnomalyDetection() {
  const [metrics, setMetrics] = useState<any>(null);
  
  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) setMetrics(calculateDashboardMetrics(dataset));
  }, []);

  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first.</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Anomaly & Safety Detection</h1>
        <p className="text-muted-foreground mt-2">Isolation Forest analysis on {metrics.rows} historical rows.</p>
      </div>

      <Card className="border-orange-200 shadow-sm bg-orange-50/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-orange-800"><ShieldAlert className="size-5" /> Detected Anomalies</CardTitle>
        </CardHeader>
        <CardContent>
           <h2 className="text-4xl font-bold text-orange-600 mb-2">{metrics.anomalies}</h2>
           {metrics.anomalies === "Insufficient Data" && <p className="text-muted-foreground text-sm">Anomaly detection requires power/energy or motion features which were not found in the uploaded dataset.</p>}
        </CardContent>
      </Card>
    </div>
  );
}
