import { createFileRoute } from "@tanstack/react-router";
import { useSmartHome } from "@/lib/smarthome/store";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/settings")({
  component: Settings,
});

function Settings() {
  const { profile, updateProfile, resetDemo } = useSmartHome();

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Manage your SmartHome AI preferences.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Mode</CardTitle>
          <CardDescription>Currently running in {profile.mode} mode.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Demo Mode</Label>
              <p className="text-sm text-muted-foreground">Generate fake sensor data instead of connecting to real hardware.</p>
            </div>
            <Switch 
              checked={profile.mode === "demo"} 
              onCheckedChange={(c) => updateProfile({ mode: c ? "demo" : "live" })} 
            />
          </div>
          
          <div className="pt-4 border-t">
            <Button variant="destructive" onClick={resetDemo}>Reset Demo Data</Button>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Privacy</CardTitle>
          <CardDescription>Data control and sharing.</CardDescription>
        </CardHeader>
        <CardContent>
           <p className="text-sm text-muted-foreground mb-4">
             Your data is processed locally using ambient sensors (no cameras or microphones). We do not send your raw routine data to external servers without your permission.
           </p>
           <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Cloud ML Sync</Label>
              <p className="text-sm text-muted-foreground">Allow advanced AI anomaly detection in the cloud.</p>
            </div>
            <Switch checked={false} disabled />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

