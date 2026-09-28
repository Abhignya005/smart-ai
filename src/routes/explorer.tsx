import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { loadDataset } from "@/lib/datasetUtils";
import { Database, AlertTriangle } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Link } from "@tanstack/react-router";

export const Route = createFileRoute("/explorer")({
  component: DatasetExplorer,
});

function DatasetExplorer() {
  const [dataset, setDataset] = useState<any>(null);

  useEffect(() => {
      setDataset(loadDataset());
  }, []);

  if (!dataset) {
      return (
          <div className="space-y-6 h-[80vh] flex flex-col items-center justify-center">
              <Database className="size-16 text-muted-foreground/30 mb-4" />
              <h2 className="text-2xl font-bold">No Dataset Found</h2>
              <p className="text-muted-foreground">Please upload a dataset in the Data Ingestion tab first.</p>
              <Button asChild className="mt-4"><Link to="/ingestion">Go to Data Ingestion</Link></Button>
          </div>
      );
  }

  // Display only top 10 rows
  const displayData = dataset.data.slice(0, 10);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dataset Explorer</h1>
        <p className="text-muted-foreground mt-2">Inspect the raw ingested data ({dataset.filename}) before downstream analysis.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Total Records</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{dataset.data.length.toLocaleString()}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Total Features</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{dataset.headers.length}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Status</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold text-green-600">ML Ready</div></CardContent></Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Raw Data Preview</CardTitle>
          <CardDescription>Showing top 10 rows</CardDescription>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                {dataset.headers.map((h: string) => (
                    <TableHead key={h} className="whitespace-nowrap">{h}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
                {displayData.map((row: any, i: number) => (
                    <TableRow key={i}>
                        {dataset.headers.map((h: string) => (
                            <TableCell key={h} className="whitespace-nowrap text-sm">{row[h] !== undefined && row[h] !== null ? row[h].toString() : ''}</TableCell>
                        ))}
                    </TableRow>
                ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
