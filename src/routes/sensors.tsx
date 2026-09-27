import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Database, FileText, Activity } from "lucide-react";

export const Route = createFileRoute("/sensors")({
  component: DatasetAnalysis,
});

function DatasetAnalysis() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/dataset-summary')
      .then(res => res.json())
      .then(json => setData(json))
      .catch(err => console.error(err));
  }, []);

  if (!data) return <div className="p-8">Loading Dataset Summary...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dataset Analysis</h1>
        <p className="text-muted-foreground mt-2">Overview of the synthetic_smarthome_data.csv training dataset.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Samples</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.rows.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">15-minute intervals</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Features</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.columns.length}</div>
            <p className="text-xs text-muted-foreground">Columns mapped</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Time Range</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-sm font-bold mt-1">{data.time_range}</div>
            <p className="text-xs text-muted-foreground mt-1">30 days of coverage</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Activity Class Distribution</CardTitle>
            <CardDescription>Number of samples per target class</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(data.activities).map(([activity, count]: any) => (
                <div key={activity} className="flex items-center justify-between">
                  <div className="font-medium">{activity}</div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-muted-foreground">{count.toLocaleString()} samples</span>
                    <div className="w-32 h-2 bg-secondary rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary" 
                        style={{ width: `${(count / data.rows) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Feature Columns</CardTitle>
            <CardDescription>Raw dataset inputs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {data.columns.map((col: string) => (
                <div key={col} className="bg-secondary text-secondary-foreground px-3 py-1 rounded-md text-sm">
                  {col}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
