import os

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

ingestion_content = """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CloudUpload, CheckCircle, FileUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useState, useRef, useEffect } from "react";
import Papa from "papaparse";
import * as XLSX from "xlsx";
import { toast } from "sonner";
import { saveDataset } from "@/lib/datasetUtils";

export const Route = createFileRoute("/ingestion")({
  component: DataIngestion,
});

function DataIngestion() {
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [datasetMeta, setDatasetMeta] = useState<any>(null);

  useEffect(() => {
      const existing = localStorage.getItem('smarthome_dataset');
      if (existing) {
          const parsed = JSON.parse(existing);
          setDatasetMeta({
              filename: parsed.filename,
              rows: parsed.data.length,
              columns: parsed.headers.length,
              features: detectFeatures(parsed.headers),
              quality: calculateQuality(parsed.data, parsed.headers)
          });
      }
  }, []);

  const detectFeatures = (headers: string[]) => {
      const h = headers.map(x => x.toLowerCase());
      return {
          timestamp: h.some(x => x.includes('time') || x.includes('date')),
          activity: h.some(x => x.includes('activity')),
          room: h.some(x => x.includes('room') || x.includes('location')),
          motion: h.some(x => x.includes('motion') || x.includes('pir')),
          door: h.some(x => x.includes('door') || x.includes('contact')),
          light: h.some(x => x.includes('light') || x.includes('lux')),
          appliance: h.some(x => x.includes('tv') || x.includes('fridge') || x.includes('oven') || x.includes('microwave')),
          power: h.some(x => x.includes('power') || x.includes('energy') || x.includes('kw')),
      };
  };

  const calculateQuality = (data: any[], headers: string[]) => {
      let missingCount = 0;
      data.forEach(row => {
          headers.forEach(h => {
              if (row[h] === undefined || row[h] === null || row[h] === '') {
                  missingCount++;
              }
          });
      });
      const totalCells = data.length * headers.length;
      const pct = totalCells > 0 ? ((totalCells - missingCount) / totalCells) * 100 : 0;
      return { score: pct.toFixed(1), missing: missingCount };
  };

  const processCsvFile = (file: File) => {
    setLoading(true);
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const data = results.data;
        const headers = results.meta.fields || [];
        finalizeUpload(file.name, headers, data);
      },
      error: (error) => {
        console.error(error);
        setLoading(false);
        toast.error("Failed to parse CSV file.");
      }
    });
  };

  const processExcelFile = async (file: File) => {
      setLoading(true);
      try {
          const buffer = await file.arrayBuffer();
          const workbook = XLSX.read(buffer, { type: "array" });
          const firstSheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheetName];
          const data = XLSX.utils.sheet_to_json(worksheet);
          
          if (data.length > 0) {
              const headers = Object.keys(data[0] as object);
              finalizeUpload(file.name, headers, data);
          } else {
              toast.error("Excel file is empty.");
              setLoading(false);
          }
      } catch (err) {
          console.error(err);
          toast.error("Failed to parse Excel file.");
          setLoading(false);
      }
  };

  const finalizeUpload = (filename: string, headers: string[], data: any[]) => {
      saveDataset(filename, headers, data);
        
      const features = detectFeatures(headers);
      const quality = calculateQuality(data, headers);
      
      setDatasetMeta({
          filename: filename,
          rows: data.length,
          columns: headers.length,
          features,
          quality
      });
      
      setLoading(false);
      toast.success(`Successfully loaded ${data.length} actual records from ${filename}`);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
        const file = e.target.files[0];
        const lowerName = file.name.toLowerCase();
        
        if (lowerName.endsWith('.csv') || lowerName.endsWith('.txt')) {
             processCsvFile(file);
        } else if (lowerName.endsWith('.xlsx') || lowerName.endsWith('.xls')) {
             processExcelFile(file);
        } else {
             toast.error("Please upload a .csv or .xlsx file.");
        }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Upload Historical Activity Data</h1>
          <p className="text-muted-foreground mt-2 max-w-2xl">Upload a CSV or Excel dataset containing anonymous ambient activity records. The platform analyzes the historical data to learn personal routines and activity patterns.</p>
        </div>
      </div>

      <input 
        type="file" 
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
                <h3 className="font-semibold text-lg">Upload Your Actual Dataset</h3>
                <p className="text-sm text-muted-foreground">Drop CSV or Excel file here to begin real processing.</p>
                <div className="flex gap-2 mt-2 justify-center">
                    <Badge variant="outline">.csv</Badge>
                    <Badge variant="outline">.xlsx</Badge>
                </div>
              </div>
              <Button onClick={() => fileInputRef.current?.click()} disabled={loading}>
                  {loading ? "Parsing Data..." : "Choose File"}
              </Button>
            </CardContent>
          </Card>
      ) : (
          <Card className="border-green-200 shadow-sm">
             <CardHeader className="bg-green-50/50 pb-4 border-b">
                 <CardTitle className="flex items-center gap-2 text-green-800 text-lg">
                    <CheckCircle className="size-5" /> Dataset Successfully Processed
                 </CardTitle>
             </CardHeader>
             <CardContent className="pt-6 space-y-6">
                 <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                     <div><p className="text-xs text-muted-foreground mb-1">Dataset</p><p className="font-bold text-sm truncate">{datasetMeta.filename}</p></div>
                     <div><p className="text-xs text-muted-foreground mb-1">Actual Rows</p><p className="font-bold">{datasetMeta.rows.toLocaleString()}</p></div>
                     <div><p className="text-xs text-muted-foreground mb-1">Columns</p><p className="font-bold">{datasetMeta.columns}</p></div>
                     <div><p className="text-xs text-muted-foreground mb-1">Data Quality</p><p className="font-bold text-green-600">{datasetMeta.quality.score}%</p></div>
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
                 </div>

                 <div className="flex justify-end gap-3 pt-4 border-t mt-6">
                     <Button variant="destructive" onClick={() => { localStorage.removeItem('smarthome_dataset'); setDatasetMeta(null); }}>Remove File & Clear Data</Button>
                 </div>
             </CardContent>
          </Card>
      )}
    </div>
  );
}
"""

with open(os.path.join(ROUTES_DIR, "ingestion.tsx"), "w", encoding="utf-8") as f:
    f.write(ingestion_content)

print("Fixed ingestion to parse real datasets instead of intercepting them for the demo.")
