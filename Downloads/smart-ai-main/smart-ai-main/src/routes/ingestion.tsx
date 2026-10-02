import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CloudUpload, CheckCircle, AlertTriangle, ArrowRight, FileCheck, Layers, RefreshCw, Cpu, Sparkles, Download, FileSpreadsheet, FileCode } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import { getOrFetchDataset, fetchLatestDataset } from "@/lib/datasetUtils";

export const Route = createFileRoute("/ingestion")({
  component: DataIngestion,
});

function DataIngestion() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isDragging, setIsDragging] = useState(false);
  const [uploadStage, setUploadStage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Metadata returned by backend
  const [datasetMeta, setDatasetMeta] = useState<any>(null);

  // Column Mapping state
  const [selectedPersonCol, setSelectedPersonCol] = useState<string>("");
  const [selectedTimeCol, setSelectedTimeCol] = useState<string>("");
  const [selectedActCol, setSelectedActCol] = useState<string>("");
  const [selectedRoomCol, setSelectedRoomCol] = useState<string>("");
  const [mappingSaving, setMappingSaving] = useState(false);
  const [training, setTraining] = useState(false);
  const [trainMetrics, setTrainMetrics] = useState<any>(null);

  const handleTrainModel = async () => {
    try {
      setTraining(true);
      const res = await fetch("http://localhost:8000/api/train-model", {
        method: "POST",
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setTrainMetrics(data.metrics);
        await fetchLatestDataset();
        toast.success(data.message || "Model trained successfully!");
      } else {
        toast.error(data.error || "Training failed.");
      }
    } catch (e) {
      toast.error("Network error during model training.");
    } finally {
      setTraining(false);
    }
  };

  useEffect(() => {
    fetchCurrentMeta();
  }, []);

  const fetchCurrentMeta = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/current-dataset-meta");
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.metadata && data.metadata.is_uploaded) {
          applyMetadata(data.metadata);
        }
      }
    } catch (e) {
      console.error("Could not fetch dataset meta", e);
    }
  };

  const applyMetadata = (meta: any) => {
    setDatasetMeta(meta);
    setSelectedPersonCol(meta.person_column || "");
    setSelectedTimeCol(meta.timestamp_column || "");
    setSelectedActCol(meta.activity_column || "");
    setSelectedRoomCol(meta.room_column || "");
  };

  const uploadFileToBackend = async (file: File) => {
    setErrorMsg(null);
    setLoading(true);

    // Validate supported extension
    const name = file.name.toLowerCase();
    const validExts = [".csv", ".xlsx", ".xls", ".json", ".parquet", ".tsv", ".txt"];
    const isValid = validExts.some((ext) => name.endsWith(ext));

    if (!isValid) {
      setErrorMsg("Unsupported file format. Please upload CSV, Excel, JSON, Parquet, TSV, or TXT.");
      setLoading(false);
      return;
    }

    try {
      // Step 1: Uploading
      setUploadStage("Uploading file to ML backend...");
      const formData = new FormData();
      formData.append("file", file);

      // Step 2: Processing
      setTimeout(() => setUploadStage("Processing dataset structure..."), 400);

      const res = await fetch("http://localhost:8000/api/ingest-document", {
        method: "POST",
        body: formData,
      });

      // Step 3: Validating
      setUploadStage("Validating records & detecting columns...");

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || "Dataset processing failed.");
      }

      // Step 4: Preparing features
      setUploadStage("Preparing ML features...");
      await new Promise((r) => setTimeout(r, 400));

      // Step 5: Completed
      setUploadStage("Completed ✓");
      applyMetadata(data);
      await fetchLatestDataset();
      toast.success(`Successfully ingested ${data.rows.toLocaleString()} records from ${file.name}`);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to upload and process dataset.");
      toast.error(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFileToBackend(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      uploadFileToBackend(e.dataTransfer.files[0]);
    }
  };

  const handleApplyMapping = async () => {
    setMappingSaving(true);
    try {
      const res = await fetch("http://localhost:8000/api/map-columns", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          person_id: selectedPersonCol || undefined,
          timestamp: selectedTimeCol || undefined,
          activity: selectedActCol || undefined,
          room: selectedRoomCol || undefined,
        }),
      });
      const data = await res.json();
      if (data.success) {
        applyMetadata(data.metadata);
        await fetchLatestDataset();
        toast.success("Column mappings confirmed and applied to ML pipeline!");
      } else {
        toast.error(data.error || "Failed to map columns");
      }
    } catch (e: any) {
      toast.error(e.message || "Failed to connect to backend");
    } finally {
      setMappingSaving(false);
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Upload Your Activity Dataset</h1>
        <p className="text-muted-foreground mt-1 text-sm max-w-2xl">
          Upload a structured smart-home activity dataset for analysis. Supports multi-format data ingestion, automated column detection, schema normalization, and ML baseline alignment.
        </p>
      </div>

      {/* Download Sample Datasets Card */}
      <Card className="bg-gradient-to-r from-primary/5 via-primary/10 to-transparent border-primary/20 shadow-sm">
        <CardContent className="p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Sparkles className="size-4 text-primary" />
              <span className="font-semibold text-sm">Need a test dataset?</span>
              <Badge variant="secondary" className="text-xs">Ready to use</Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Download pre-configured multi-person smart home sample datasets to test activity recognition, routines, and anomalies.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <a
              href="/sample_10_records.csv"
              download="sample_10_records.csv"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 text-xs font-semibold transition-colors shadow-sm"
            >
              <FileSpreadsheet className="size-4" />
              <span>Download 10 Records (CSV)</span>
              <Download className="size-3 ml-1" />
            </a>
            <a
              href="/sample_10_records.xlsx"
              download="sample_10_records.xlsx"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-background border hover:bg-accent text-xs font-medium transition-colors shadow-sm"
            >
              <FileSpreadsheet className="size-4 text-blue-600" />
              <span>10 Records (.xlsx)</span>
              <Download className="size-3 text-muted-foreground ml-1" />
            </a>
            <a
              href="/sample_10_records.json"
              download="sample_10_records.json"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-background border hover:bg-accent text-xs font-medium transition-colors shadow-sm"
            >
              <FileCode className="size-4 text-amber-600" />
              <span>10 Records (.json)</span>
              <Download className="size-3 text-muted-foreground ml-1" />
            </a>
          </div>
        </CardContent>
      </Card>

      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        accept=".csv,.xlsx,.xls,.json,.parquet,.tsv,.txt"
        onChange={handleFileSelect}
      />

      {/* Drag & Drop Upload Zone */}
      <Card
        className={`border-dashed border-2 transition-colors cursor-pointer ${
          isDragging
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50 bg-muted/5"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !loading && fileInputRef.current?.click()}
      >
        <CardContent className="flex flex-col items-center justify-center py-12 space-y-4">
          <div className="bg-primary/10 p-4 rounded-full">
            <CloudUpload className="size-8 text-primary" />
          </div>

          <div className="text-center space-y-1">
            <h3 className="font-semibold text-lg">Upload Your Activity Dataset</h3>
            <p className="text-sm text-muted-foreground">Drag & drop your file here, or click to browse</p>
          </div>

          <Button
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            disabled={loading}
          >
            {loading ? "Processing..." : "Choose File"}
          </Button>

          <div className="text-xs text-muted-foreground pt-2 text-center">
            <p className="font-medium text-foreground mb-1">Supported formats:</p>
            <p className="font-mono text-muted-foreground">CSV • Excel • JSON • Parquet • TSV • TXT</p>
          </div>
        </CardContent>
      </Card>

      {/* Upload Progress Status */}
      {loading && uploadStage && (
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <RefreshCw className="size-4 animate-spin text-primary" />
              <span className="text-sm font-medium">{uploadStage}</span>
            </div>
            <span className="text-xs font-mono text-muted-foreground">Backend Processing</span>
          </CardContent>
        </Card>
      )}

      {/* Error Banner */}
      {errorMsg && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="py-4 flex items-center gap-3 text-destructive">
            <AlertTriangle className="size-5 shrink-0" />
            <div className="text-sm">
              <p className="font-semibold">Dataset Ingestion Notice</p>
              <p>{errorMsg}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dataset Details & Preview Section */}
      {datasetMeta && (
        <div className="space-y-6 animate-in fade-in">
          {/* Status Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b gap-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="size-5 text-green-600" />
              <h2 className="text-lg font-bold">Active Dataset Details</h2>
              <Badge variant="outline" className="ml-2 font-mono">
                {datasetMeta.format}
              </Badge>
            </div>

            <Button
              size="sm"
              className="gap-2"
              onClick={() => navigate({ to: "/" })}
            >
              Go to ML Dashboard <ArrowRight className="size-4" />
            </Button>
          </div>

          {/* Core Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card className="shadow-sm">
              <CardContent className="pt-4">
                <p className="text-xs text-muted-foreground uppercase font-semibold">Dataset Name</p>
                <p className="text-base font-bold truncate mt-1" title={datasetMeta.filename}>
                  {datasetMeta.filename}
                </p>
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardContent className="pt-4">
                <p className="text-xs text-muted-foreground uppercase font-semibold">Total Rows</p>
                <p className="text-2xl font-bold mt-1">{datasetMeta.rows?.toLocaleString()}</p>
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardContent className="pt-4">
                <p className="text-xs text-muted-foreground uppercase font-semibold">Columns</p>
                <p className="text-2xl font-bold mt-1">{datasetMeta.columns_count}</p>
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardContent className="pt-4">
                <p className="text-xs text-muted-foreground uppercase font-semibold">Detected Members</p>
                <p className="text-2xl font-bold mt-1 text-primary">
                  {datasetMeta.detected_members?.count ?? 1}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Secondary Details: Time Range, Quality, Activities */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="shadow-sm">
              <CardHeader className="pb-2 bg-muted/10 border-b">
                <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Dataset Time Span & Quality
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4 space-y-3 text-sm">
                <div>
                  <span className="text-muted-foreground text-xs block">Time Range:</span>
                  <span className="font-mono font-medium">{datasetMeta.time_range}</span>
                </div>
                <div className="border-t pt-2 flex justify-between items-center">
                  <span>Data Quality Score:</span>
                  <span className="font-bold text-green-600">{datasetMeta.quality_score}%</span>
                </div>
                <div className="flex justify-between items-center text-xs text-muted-foreground">
                  <span>Missing Values:</span>
                  <span className="font-mono">{datasetMeta.missing_values ?? 0}</span>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardHeader className="pb-2 bg-muted/10 border-b">
                <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Detected Activity Labels
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                {datasetMeta.detected_activities && datasetMeta.detected_activities.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {datasetMeta.detected_activities.map((act: string, idx: number) => (
                      <Badge key={idx} variant="secondary" className="text-xs font-medium">
                        {act}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground italic">
                    No explicit activity label column identified.
                  </p>
                )}
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardHeader className="pb-2 bg-muted/10 border-b">
                <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  ML Pipeline Suitability
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4 space-y-2 text-xs">
                {datasetMeta.suitability && (
                  <>
                    <div className="flex items-center justify-between border-b pb-1.5">
                      <span>Activity Recognition:</span>
                      <span
                        className={
                          datasetMeta.suitability.activity_recognition?.supported
                            ? "text-green-600 font-semibold"
                            : "text-muted-foreground"
                        }
                      >
                        {datasetMeta.suitability.activity_recognition?.supported ? "✓ Supported" : "⚠ Label Missing"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between border-b pb-1.5">
                      <span>Routine Discovery:</span>
                      <span
                        className={
                          datasetMeta.suitability.routine_discovery?.supported
                            ? "text-green-600 font-semibold"
                            : "text-muted-foreground"
                        }
                      >
                        {datasetMeta.suitability.routine_discovery?.supported ? "✓ Supported" : "⚠ Timestamp Missing"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between border-b pb-1.5">
                      <span>Family Mode:</span>
                      <span
                        className={
                          datasetMeta.suitability.family_analysis?.supported
                            ? "text-green-600 font-semibold"
                            : "text-muted-foreground"
                        }
                      >
                        {datasetMeta.suitability.family_analysis?.supported ? "✓ Multi-User" : "Single Person"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Spatial Room Analysis:</span>
                      <span
                        className={
                          datasetMeta.suitability.room_analysis?.supported
                            ? "text-green-600 font-semibold"
                            : "text-muted-foreground"
                        }
                      >
                        {datasetMeta.suitability.room_analysis?.supported ? "✓ Sensors Present" : "Not Available"}
                      </span>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Column Mapping Interface */}
          <Card className="shadow-sm">
            <CardHeader className="pb-3 bg-muted/10 border-b">
              <CardTitle className="text-sm font-bold flex items-center justify-between">
                <span>Column Mapping Configuration</span>
                <span className="text-xs font-normal text-muted-foreground">
                  Verify or assign column roles for the ML pipeline
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1 block">
                    Person / Member ID:
                  </label>
                  <select
                    value={selectedPersonCol}
                    onChange={(e) => setSelectedPersonCol(e.target.value)}
                    className="w-full text-sm border rounded p-1.5 bg-background"
                  >
                    <option value="">(None / Ambient Stream)</option>
                    {datasetMeta.columns?.map((col: string) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1 block">
                    Timestamp Column:
                  </label>
                  <select
                    value={selectedTimeCol}
                    onChange={(e) => setSelectedTimeCol(e.target.value)}
                    className="w-full text-sm border rounded p-1.5 bg-background"
                  >
                    <option value="">(None)</option>
                    {datasetMeta.columns?.map((col: string) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1 block">
                    Activity Target Label:
                  </label>
                  <select
                    value={selectedActCol}
                    onChange={(e) => setSelectedActCol(e.target.value)}
                    className="w-full text-sm border rounded p-1.5 bg-background"
                  >
                    <option value="">(None)</option>
                    {datasetMeta.columns?.map((col: string) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1 block">
                    Room / Location:
                  </label>
                  <select
                    value={selectedRoomCol}
                    onChange={(e) => setSelectedRoomCol(e.target.value)}
                    className="w-full text-sm border rounded p-1.5 bg-background"
                  >
                    <option value="">(Derived from sensors)</option>
                    {datasetMeta.columns?.map((col: string) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t">
                <div className="text-xs">
                  {trainMetrics ? (
                    <div className="flex items-center gap-1.5 text-green-600 font-medium">
                      <CheckCircle className="size-4 shrink-0" />
                      <span>
                        Model trained on {trainMetrics.records} records • Accuracy: {trainMetrics.accuracy}% (F1: {trainMetrics.f1_score}%)
                      </span>
                    </div>
                  ) : (
                    <span className="text-muted-foreground">
                      Train the ML model directly on this dataset's ground-truth labels.
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleTrainModel}
                    disabled={training || !datasetMeta.activity_column}
                    className="gap-2 border-primary/30 text-primary hover:bg-primary/10"
                    title={!datasetMeta.activity_column ? "Requires mapped activity column" : "Fit Random Forest model on this dataset"}
                  >
                    {training ? (
                      <>
                        <RefreshCw className="size-3.5 animate-spin" /> Training Model...
                      </>
                    ) : (
                      <>
                        <Cpu className="size-3.5" /> Train / Update Model
                      </>
                    )}
                  </Button>

                  <Button size="sm" onClick={handleApplyMapping} disabled={mappingSaving}>
                    {mappingSaving ? "Applying..." : "Confirm & Apply Mapping"}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* First 10 Rows Table Preview */}
          {datasetMeta.preview && datasetMeta.preview.length > 0 && (
            <Card className="shadow-sm">
              <CardHeader className="pb-2 bg-muted/10 border-b">
                <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex justify-between items-center">
                  <span>First 10 Rows Preview</span>
                  <span className="font-mono text-muted-foreground font-normal">
                    {datasetMeta.rows?.toLocaleString()} Total Records
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4 overflow-x-auto">
                <table className="w-full text-xs text-left border-collapse">
                  <thead>
                    <tr className="border-b bg-muted/20">
                      {datasetMeta.columns?.map((col: string) => (
                        <th key={col} className="p-2 font-mono font-semibold text-foreground whitespace-nowrap">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {datasetMeta.preview.map((row: any, i: number) => (
                      <tr key={i} className="border-b hover:bg-muted/10 transition-colors">
                        {datasetMeta.columns?.map((col: string) => (
                          <td key={col} className="p-2 font-mono whitespace-nowrap text-muted-foreground">
                            {row[col] !== undefined && row[col] !== null && row[col] !== ""
                              ? String(row[col])
                              : "—"}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
