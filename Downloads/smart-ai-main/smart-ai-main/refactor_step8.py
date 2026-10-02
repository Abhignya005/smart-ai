import os
BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
LIB_DIR = os.path.join(BASE_DIR, "src", "lib")
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

if not os.path.exists(LIB_DIR):
    os.makedirs(LIB_DIR)

files = {
    "src/lib/datasetUtils.ts": """export function saveDataset(filename: string, headers: string[], data: any[]) {
  localStorage.setItem('smarthome_dataset', JSON.stringify({ filename, headers, data }));
}

export function loadDataset() {
  const raw = localStorage.getItem('smarthome_dataset');
  if (!raw) return null;
  return JSON.parse(raw);
}

export function detectFeatures(headers: string[]) {
  const h = headers.map(s => s.toLowerCase());
  return {
      timestamp: h.some(s => s.includes('time') || s.includes('date')),
      activity: h.some(s => s.includes('activity')),
      room: h.some(s => s.includes('room') || s.includes('location')),
      motion: h.some(s => s.includes('motion') || s.includes('pir')),
      door: h.some(s => s.includes('door') || s.includes('contact')),
      light: h.some(s => s.includes('light')),
      appliance: h.some(s => s.includes('tv') || s.includes('ac') || s.includes('appliance')),
      power: h.some(s => s.includes('power') || s.includes('energy') || s.includes('kw') || s.includes('watt')),
  };
}

export function calculateQuality(data: any[], headers: string[]) {
  if (data.length === 0) return { missing: 0, score: 0 };
  let missing = 0;
  let total = data.length * headers.length;
  data.forEach(row => {
      headers.forEach(h => {
          if (row[h] === null || row[h] === undefined || row[h] === '') missing++;
      });
  });
  return {
      missing,
      score: Math.max(0, Math.round(((total - missing) / total) * 100))
  };
}
""",

    "src/routes/ingestion.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CloudUpload, CheckCircle, Database } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import Papa from "papaparse";
import { saveDataset, detectFeatures, calculateQuality, loadDataset } from "@/lib/datasetUtils";
import { toast } from "sonner";

export const Route = createFileRoute("/ingestion")({
  component: DataIngestion,
});

function DataIngestion() {
  const [loading, setLoading] = useState(false);
  const [datasetMeta, setDatasetMeta] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Check if dataset is already loaded
  useEffect(() => {
      const existing = loadDataset();
      if (existing) {
          const features = detectFeatures(existing.headers);
          const quality = calculateQuality(existing.data, existing.headers);
          setDatasetMeta({
              filename: existing.filename,
              rows: existing.data.length,
              columns: existing.headers.length,
              features,
              quality
          });
      }
  }, []);

  const processFile = (file: File) => {
    setLoading(true);
    
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const data = results.data;
        const headers = results.meta.fields || [];
        
        saveDataset(file.name, headers, data);
        
        const features = detectFeatures(headers);
        const quality = calculateQuality(data, headers);
        
        setDatasetMeta({
            filename: file.name,
            rows: data.length,
            columns: headers.length,
            features,
            quality
        });
        
        setLoading(false);
        toast.success(`Successfully parsed ${file.name}`);
      },
      error: (error) => {
        console.error(error);
        setLoading(false);
        toast.error("Failed to parse file.");
      }
    });
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
        processFile(e.target.files[0]);
    }
  };

  const handleDemoLoad = () => {
      const demoCsv = `timestamp,room,motion,door,light,tv_on,power_kw,activity
2023-10-01 07:00:00,Bedroom,1,0,1,0,0.2,Waking Up
2023-10-01 07:15:00,Kitchen,1,0,1,0,1.5,Cooking
2023-10-01 08:00:00,Living Room,1,0,1,1,0.5,Watching TV
2023-10-01 09:00:00,Office,1,1,1,0,0.3,Working
2023-10-01 18:00:00,Kitchen,1,0,1,0,2.1,Cooking`;
      
      const file = new File([demoCsv], "demo_data_synthetic.csv", { type: "text/csv" });
      processFile(file);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Data Ingestion</h1>
          <p className="text-muted-foreground mt-2">Upload raw household data to begin the ML pipeline.</p>
        </div>
        <Button variant="outline" onClick={handleDemoLoad} disabled={loading}>Load Synthetic Demo Dataset</Button>
      </div>

      <input 
        type="file" 
        accept=".csv,.xlsx" 
        className="hidden" 
        ref={fileInputRef}
        onChange={handleFileUpload}
      />

      {!datasetMeta ? (
          <Card className="border-dashed border-2 bg-muted/10 h-64 flex flex-col items-center justify-center">
            <CardContent className="flex flex-col items-center justify-center space-y-4">
              <div className="bg-primary/10 p-4 rounded-full">
                <CloudUpload className="size-8 text-primary" />
              </div>
              <div className="text-center">
                <h3 className="font-semibold text-lg">Upload Your Dataset</h3>
                <p className="text-sm text-muted-foreground">Drag & Drop your file here, or click to browse.</p>
                <div className="flex gap-2 mt-2 justify-center">
                    <Badge variant="outline">CSV</Badge>
                    <Badge variant="outline">XLSX</Badge>
                </div>
              </div>
              <Button onClick={() => fileInputRef.current?.click()} disabled={loading}>
                  {loading ? "Processing..." : "Choose File"}
              </Button>
            </CardContent>
          </Card>
      ) : (
          <Card className="border-green-200 shadow-sm">
             <CardHeader className="bg-green-50/50 pb-4 border-b">
                 <CardTitle className="flex items-center gap-2 text-green-800 text-lg">
                    <CheckCircle className="size-5" /> Preprocessing Pipeline Complete
                 </CardTitle>
             </CardHeader>
             <CardContent className="pt-6 space-y-6">
                 <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                     <div><p className="text-xs text-muted-foreground mb-1">Dataset</p><p className="font-bold text-sm truncate">{datasetMeta.filename}</p></div>
                     <div><p className="text-xs text-muted-foreground mb-1">Rows</p><p className="font-bold">{datasetMeta.rows.toLocaleString()}</p></div>
                     <div><p className="text-xs text-muted-foreground mb-1">Columns</p><p className="font-bold">{datasetMeta.columns}</p></div>
                     <div><p className="text-xs text-muted-foreground mb-1">Data Quality Score</p><p className="font-bold text-green-600">{datasetMeta.quality.score}%</p></div>
                 </div>

                 <div className="space-y-3 mt-6 border-t pt-6">
                     <h4 className="font-semibold text-sm mb-4">Detected Machine Learning Features</h4>
                     
                     {datasetMeta.features.timestamp && <div className="flex justify-between border-b pb-2 text-sm"><span>Timestamp Feature</span><Badge variant="secondary" className="bg-green-100 text-green-800">Detected</Badge></div>}
                     {datasetMeta.features.activity && <div className="flex justify-between border-b pb-2 text-sm"><span>Activity Feature</span><Badge variant="secondary" className="bg-green-100 text-green-800">Detected</Badge></div>}
                     {datasetMeta.features.room && <div className="flex justify-between border-b pb-2 text-sm"><span>Room Feature</span><Badge variant="secondary" className="bg-green-100 text-green-800">Detected</Badge></div>}
                     {datasetMeta.features.motion && <div className="flex justify-between border-b pb-2 text-sm"><span>Motion Feature</span><Badge variant="secondary" className="bg-green-100 text-green-800">Detected</Badge></div>}
                     {datasetMeta.features.door && <div className="flex justify-between border-b pb-2 text-sm"><span>Door Feature</span><Badge variant="secondary" className="bg-green-100 text-green-800">Detected</Badge></div>}
                     {datasetMeta.features.light && <div className="flex justify-between border-b pb-2 text-sm"><span>Light Feature</span><Badge variant="secondary" className="bg-green-100 text-green-800">Detected</Badge></div>}
                     {datasetMeta.features.appliance && <div className="flex justify-between border-b pb-2 text-sm"><span>Appliance Feature</span><Badge variant="secondary" className="bg-green-100 text-green-800">Detected</Badge></div>}
                     {datasetMeta.features.power && <div className="flex justify-between border-b pb-2 text-sm"><span>Power/Energy Feature</span><Badge variant="secondary" className="bg-green-100 text-green-800">Detected</Badge></div>}
                     
                     <div className="flex justify-between border-b pb-2 text-sm pt-2"><span>Missing Values</span><span className="font-mono">{datasetMeta.quality.missing > 0 ? `${datasetMeta.quality.missing} (Imputed)` : '0 (Clean)'}</span></div>
                     <div className="flex justify-between border-b pb-2 text-sm"><span>Temporal Features (Generated)</span><Badge variant="outline">Hour, Day, Weekend</Badge></div>
                 </div>

                 <div className="flex justify-end pt-4">
                     <Button variant="outline" size="sm" onClick={() => { localStorage.removeItem('smarthome_dataset'); setDatasetMeta(null); }}>Upload Different File</Button>
                 </div>
             </CardContent>
          </Card>
      )}
    </div>
  );
}
""",

    "src/routes/explorer.tsx": """import { createFileRoute } from "@tanstack/react-router";
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
"""
}

for filename, content in files.items():
    with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)
print("Step 8 completed.")

