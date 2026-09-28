import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { EyeOff, ShieldCheck, Database, CameraOff, MicOff } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/settings")({
  component: PrivacySettings,
});

function PrivacySettings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Privacy & Settings</h1>
        <p className="text-muted-foreground mt-2">Configure platform rules and review privacy constraints.</p>
      </div>

      <Card className="border-green-200 shadow-sm bg-green-50/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-800"><ShieldCheck className="size-5" /> Privacy First Architecture</CardTitle>
          <CardDescription>This platform is fundamentally designed to protect human privacy.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
           <div className="flex flex-wrap gap-4">
               <Badge className="bg-green-100 text-green-800 text-sm py-1 flex items-center gap-1 hover:bg-green-100"><CameraOff className="size-4"/> NO CAMERA REQUIRED</Badge>
               <Badge className="bg-green-100 text-green-800 text-sm py-1 flex items-center gap-1 hover:bg-green-100"><MicOff className="size-4"/> NO MICROPHONE REQUIRED</Badge>
               <Badge className="bg-green-100 text-green-800 text-sm py-1 flex items-center gap-1 hover:bg-green-100"><EyeOff className="size-4"/> NO FACIAL RECOGNITION</Badge>
           </div>
           
           <p className="text-sm leading-relaxed">
             The Activity Recognition and Routine Discovery models operate entirely on non-visual, anonymous ambient vectors (such as total energy draw, binary door contacts, and PIR motion counts). This approach extracts high-fidelity actionable intelligence without compromising the sanctity of the household.
           </p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
              <CardHeader><CardTitle>Data Retention</CardTitle></CardHeader>
              <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">Uploaded datasets are kept purely for active session analysis. They are not permanently stored or used to train external foundation models.</p>
                  <Badge variant="outline">Session-Only Storage Active</Badge>
              </CardContent>
          </Card>
          <Card>
              <CardHeader><CardTitle>Live Data Simulator</CardTitle><CardDescription>For Demonstration Purposes</CardDescription></CardHeader>
              <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">Injects synthetic sensor events directly into the context buffer to test anomaly thresholds and forecasting.</p>
                  <Badge className="bg-purple-100 text-purple-800 hover:bg-purple-100">Live Simulator Disabled</Badge>
              </CardContent>
          </Card>
      </div>
    </div>
  );
}
