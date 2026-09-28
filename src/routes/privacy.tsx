import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ShieldCheck, Check } from "lucide-react";

export const Route = createFileRoute("/privacy")({ component: PrivacyCenter });

function PrivacyCenter() {
  return (
    <div className="space-y-10 pb-16 animate-in fade-in duration-500">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Privacy Center</h1>
        <p className="text-muted-foreground text-lg mt-2">How PersonaSense AI protects your personal data.</p>
      </div>

      <Card className="bg-emerald-50/50 border-emerald-200 shadow-sm">
          <CardHeader>
              <CardTitle className="flex items-center gap-2 text-emerald-800"><ShieldCheck className="size-6"/> Privacy by Design</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">No camera required</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">No microphone required</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">No facial recognition</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">No wearable required</span></div>
              </div>
              <div className="space-y-3">
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">No live IoT connection</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">Historical dataset analysis only</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">User-controlled uploaded data</span></div>
                  <div className="flex items-center gap-3 text-emerald-900"><Check className="size-5 text-emerald-600"/><span className="font-medium">Explainable ML predictions</span></div>
              </div>
          </CardContent>
      </Card>

      <Card className="shadow-sm">
          <CardHeader>
              <CardTitle>What data is being analyzed?</CardTitle>
          </CardHeader>
          <CardContent>
              <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                  The platform uses mathematical models to find patterns in anonymous ambient data. 
                  These are simply columns in a CSV file, not live connections to your house.
              </p>
              <div className="flex flex-wrap gap-2">
                  {['Timestamp', 'Room', 'Motion', 'Light', 'Door Status', 'Power (kW)', 'Activity Label'].map(f => (
                      <div key={f} className="px-3 py-1.5 bg-slate-100 rounded-md border border-slate-200 text-sm font-medium text-slate-700">{f}</div>
                  ))}
              </div>
              <p className="text-xs text-slate-400 mt-6 font-bold uppercase tracking-widest text-center">NOT A SMART HOME CONTROL SYSTEM</p>
          </CardContent>
      </Card>
    </div>
  );
}
