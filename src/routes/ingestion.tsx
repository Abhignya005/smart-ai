import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud, CheckCircle2, FileText, Activity, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/ingestion")({
  component: DataIngestion,
});

function DataIngestion() {
  const [file, setFile] = useState<File | null>(null);
  const [step, setStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [dataScore, setDataScore] = useState(94);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;
    setFile(uploadedFile);
    setStep(2);
    setIsProcessing(true);
    setTimeout(() => {
        setIsProcessing(false);
        setStep(3);
        toast.success("Data successfully extracted & validated.");
    }, 2000);
  };

  const loadDemo = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setFile(new File([], "demo_smarthome_data.csv"));
      setIsProcessing(false);
      setStep(3);
      toast.success("Demo Dataset Loaded");
    }, 1000);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Data Ingestion</h1>
          <p className="text-muted-foreground mt-2">Upload raw household data to begin the ML pipeline.</p>
        </div>
        <Button variant="outline" onClick={loadDemo}>Load Demo Dataset</Button>
      </div>

      {step <= 2 && (
        <Card className="border-dashed border-2 bg-muted/20">
          <CardContent className="flex flex-col items-center justify-center p-12 text-center space-y-4">
            <div className="rounded-full bg-primary/10 p-4">
              <UploadCloud className="size-8 text-primary" />
            </div>
            <div className="space-y-1">
              <h3 className="font-semibold text-lg">Upload Your Dataset</h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                Drag & Drop your file here, or click to browse.
              </p>
            </div>
            <div className="flex gap-2">
              <Badge variant="secondary">CSV</Badge>
              <Badge variant="secondary">XLSX</Badge>
              <Badge variant="secondary">PDF</Badge>
            </div>
            <div className="mt-6 relative">
              <Button disabled={isProcessing}>
                {isProcessing ? "Validating & Preprocessing..." : "Choose File"}
              </Button>
              <input type="file" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" accept=".csv,.xlsx,.xls,.pdf" onChange={handleFileUpload} disabled={isProcessing} />
            </div>
          </CardContent>
        </Card>
      )}

      {step === 3 && (
        <div className="space-y-6 animate-in slide-in-from-bottom-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><CheckCircle2 className="text-green-500" /> Preprocessing Pipeline Complete</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div><p className="text-sm text-muted-foreground">Dataset</p><p className="font-bold truncate">{file?.name}</p></div>
                <div><p className="text-sm text-muted-foreground">Rows</p><p className="font-bold">125,430</p></div>
                <div><p className="text-sm text-muted-foreground">Columns</p><p className="font-bold">18</p></div>
                <div><p className="text-sm text-muted-foreground">Data Quality Score</p><p className="font-bold text-green-600">{dataScore}%</p></div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm border-b pb-2"><span>Timestamp Column</span><Badge className="bg-green-100 text-green-800 hover:bg-green-100">Detected</Badge></div>
                <div className="flex justify-between items-center text-sm border-b pb-2"><span>Energy Columns</span><Badge className="bg-green-100 text-green-800 hover:bg-green-100">Detected</Badge></div>
                <div className="flex justify-between items-center text-sm border-b pb-2"><span>Motion Sensors</span><Badge className="bg-green-100 text-green-800 hover:bg-green-100">Detected</Badge></div>
                <div className="flex justify-between items-center text-sm border-b pb-2"><span>Missing Values</span><Badge variant="outline">Handled (Imputed)</Badge></div>
                <div className="flex justify-between items-center text-sm border-b pb-2"><span>Temporal Features</span><Badge variant="outline">Generated</Badge></div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
