import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Database } from "lucide-react";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/energy")({
  component: EnergyIntelligence,
});

function EnergyIntelligence() {
  const [metrics, setMetrics] = useState<any>(null);
  
  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) setMetrics(calculateDashboardMetrics(dataset));
  }, []);

  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first.</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Energy Intelligence</h1>
        <p className="text-muted-foreground mt-2">Analysis based on {metrics.rows} historical rows.</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Peak Consumption</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold text-red-500">{metrics.peakEnergy}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Status</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{metrics.peakEnergy === 'Not Available' ? 'Insufficient Data' : 'Active'}</div></CardContent></Card>
      </div>
    </div>
  );
}
