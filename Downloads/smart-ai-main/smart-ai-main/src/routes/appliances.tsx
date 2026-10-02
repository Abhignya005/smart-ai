import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Database } from "lucide-react";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/appliances")({
  component: ApplianceIntelligence,
});

function ApplianceIntelligence() {
  const [metrics, setMetrics] = useState<any>(null);
  
  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) setMetrics(calculateDashboardMetrics(dataset));
  }, []);

  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first.</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Appliance Intelligence</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Historical Appliance Usage</CardTitle>
        </CardHeader>
        <CardContent>
           {metrics.cols.applianceCol ? (
               <p>Appliance data is being analyzed from: {metrics.cols.applianceCol}</p>
           ) : (
               <p className="text-muted-foreground">Insufficient Data: No appliance features detected in the uploaded dataset.</p>
           )}
        </CardContent>
      </Card>
    </div>
  );
}
