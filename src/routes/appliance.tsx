import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud, CheckCircle2, AlertCircle, FileText, BarChart3, ShieldAlert, Zap, Activity } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export const Route = createFileRoute("/appliance")({
  component: DataIngestionRunner,
});

function DataIngestionRunner() {
  const [file, setFile] = useState<File | null>(null);
  const [step, setStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [extractedData, setExtractedData] = useState<any>(null);
  const [selectedTask, setSelectedTask] = useState<string>("activity");
  const [results, setResults] = useState<any>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;
    setFile(uploadedFile);
    setStep(2);
    setIsProcessing(true);

    const formData = new FormData();
    formData.append("file", uploadedFile);

    try {
      const res = await fetch("http://localhost:8000/api/ingest-document", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      
      if (data.success) {
        setExtractedData(data);
        setStep(4);
        toast.success("Document parsed successfully");
      } else {
        toast.error("Extraction Failed", { description: data.error });
        setStep(1);
      }
    } catch (err) {
      console.error(err);
      toast.error("Network Error", { description: "Failed to reach ML backend." });
      setStep(1);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRunTask = async () => {
    setIsProcessing(true);
    try {
      const res = await fetch("http://localhost:8000/api/run-ml-task", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          task: selectedTask,
          filename: extractedData.filename
        })
      });
      const data = await res.json();
      
      if (data.success) {
        setResults(data.results);
        setStep(8);
        toast.success("ML Analysis Complete");
      } else {
        toast.error("ML Task Failed", { description: data.error });
      }
    } catch (err) {
      console.error(err);
      toast.error("Network Error");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Data Ingestion & ML Runner</h1>
        <p className="text-muted-foreground mt-2">Upload historical data in any format to run pure machine learning analysis.</p>
      </div>

      {step <= 3 && (
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
            
            <div className="flex flex-wrap justify-center gap-2 mt-4">
              <Badge variant="secondary">CSV</Badge>
              <Badge variant="secondary">XLSX</Badge>
              <Badge variant="secondary">PDF</Badge>
              <Badge variant="secondary">DOCX</Badge>
              <Badge variant="secondary">TXT</Badge>
            </div>

            <div className="mt-6 relative">
              <Button disabled={isProcessing}>
                {isProcessing ? "Extracting Data..." : "Choose File"}
              </Button>
              <input 
                type="file" 
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
                accept=".csv,.xlsx,.xls,.pdf,.docx,.txt"
                onChange={handleFileUpload}
                disabled={isProcessing}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {step >= 4 && extractedData && step < 8 && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="text-green-500 size-5" /> 
                Extraction Successful
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">File Name</p>
                  <p className="font-medium truncate">{extractedData.filename}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Format</p>
                  <p className="font-medium uppercase">{extractedData.format}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Detected Rows</p>
                  <p className="font-medium">{extractedData.rows.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Detected Columns</p>
                  <p className="font-medium">{extractedData.columns.length}</p>
                </div>
              </div>

              <div className="border rounded-md mt-4 overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="bg-muted text-muted-foreground">
                    <tr>
                      {extractedData.columns.map((col: string) => (
                        <th key={col} className="px-4 py-2 font-medium">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {extractedData.preview.map((row: any, i: number) => (
                      <tr key={i} className="border-t">
                        {extractedData.columns.map((col: string) => (
                          <td key={col} className="px-4 py-2 truncate max-w-[150px]">{row[col]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Select ML Task</CardTitle>
              <CardDescription>Choose the machine learning pipeline to run on this dataset.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Select value={selectedTask} onValueChange={setSelectedTask}>
                <SelectTrigger className="w-full md:w-[300px]">
                  <SelectValue placeholder="Select a task" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="activity">Activity Recognition</SelectItem>
                  <SelectItem value="anomaly">Anomaly Detection</SelectItem>
                  <SelectItem value="energy">Energy Forecasting</SelectItem>
                  <SelectItem value="routine">Routine Learning</SelectItem>
                </SelectContent>
              </Select>
              
              <Button onClick={handleRunTask} disabled={isProcessing} className="w-full md:w-auto">
                {isProcessing ? "Running ML Pipeline..." : "Run ML Analysis"}
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {step === 8 && results && (
        <div className="space-y-6">
           <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">ML Analysis Results</h2>
            <Button variant="outline" onClick={() => { setStep(1); setExtractedData(null); setResults(null); }}>
              Analyze Another File
            </Button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="capitalize">{selectedTask.replace('_', ' ')} Pipeline Output</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-md overflow-auto max-h-[400px] text-xs font-mono">
                {JSON.stringify(results, null, 2)}
              </pre>
            </CardContent>
          </Card>
        </div>
      )}

    </div>
  );
}
