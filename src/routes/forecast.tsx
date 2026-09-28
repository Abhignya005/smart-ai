import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Database } from "lucide-react";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/forecast")({
  component: EnergyForecasting,
});

function EnergyForecasting() {
  const [metrics, setMetrics] = useState<any>(null);
  
  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) setMetrics(calculateDashboardMetrics(dataset));
  }, []);

  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first.</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Energy Forecasting</h1>
        </div>
        <Badge variant="outline" className="bg-blue-50 text-blue-700 py-1">Model Ready</Badge>
      </div>

      <Card>
         <CardHeader><CardTitle>Prediction</CardTitle></CardHeader>
         <CardContent>
            <h2 className="text-3xl font-bold text-blue-600 mb-2">{metrics.forecast}</h2>
            {metrics.forecast.includes('unavailable') && <p className="text-muted-foreground text-sm">Forecasting requires historical power/energy and timestamp columns.</p>}
         </CardContent>
      </Card>
    </div>
  );
}
