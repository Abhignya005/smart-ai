import os

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

files = {
    "src/routes/energy.tsx": """import { createFileRoute } from "@tanstack/react-router";
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
""",

    "src/routes/forecast.tsx": """import { createFileRoute } from "@tanstack/react-router";
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
""",

    "src/routes/appliances.tsx": """import { createFileRoute } from "@tanstack/react-router";
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
"""
}

for filename, content in files.items():
    with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)
print("Step 12 completed.")
