import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Link } from "@tanstack/react-router";
import { ArrowRight, Activity, Zap, ShieldAlert, Cpu } from "lucide-react";

export const Route = createFileRoute("/")({
  component: DashboardOverview,
});

function DashboardOverview() {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/metrics')
      .then(res => res.json())
      .then(json => setMetrics(json))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">ML Overview Dashboard</h1>
        <p className="text-muted-foreground mt-2">Privacy-Preserving Machine Learning for Human Activity and Energy Intelligence.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        
        <Card className="hover:border-primary transition-colors cursor-pointer" onClick={() => window.location.href='/activity'}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Activity Recognition</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics ? `${(metrics.Activity_Recognition['Random Forest'].Accuracy * 100).toFixed(1)}%` : '...'}</div>
            <p className="text-xs text-muted-foreground">Random Forest Accuracy</p>
          </CardContent>
        </Card>

        <Card className="hover:border-primary transition-colors cursor-pointer" onClick={() => window.location.href='/appliance'}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Energy Forecasting</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics ? `${metrics.Energy_Forecasting['XGBoost'].MAE} kW` : '...'}</div>
            <p className="text-xs text-muted-foreground">XGBoost Mean Absolute Error</p>
          </CardContent>
        </Card>

        <Card className="hover:border-primary transition-colors cursor-pointer" onClick={() => window.location.href='/anomalies'}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Anomaly Detection</CardTitle>
            <ShieldAlert className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Active</div>
            <p className="text-xs text-muted-foreground">Isolation Forest Model</p>
          </CardContent>
        </Card>

        <Card className="hover:border-primary transition-colors cursor-pointer" onClick={() => window.location.href='/sensors'}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Dataset Engine</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2,880</div>
            <p className="text-xs text-muted-foreground">Training Samples Loaded</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Welcome to SmartHome ML</CardTitle>
          <CardDescription>System Architecture Overview</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-sm">
            <p>This project has been completely transformed into a <strong>Pure Machine Learning Platform</strong>. It no longer relies on physical IoT hardware, mock sensors, or fake JSON states.</p>
            <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
              <li><strong>The Dataset:</strong> The system is trained on 30 days of historical sensor and energy data (synthetic for this demo).</li>
              <li><strong>Activity Recognition:</strong> Uses a trained Random Forest model to predict user activities based on ambient movement and appliance power usage.</li>
              <li><strong>Anomaly Detection:</strong> Employs an Isolation Forest algorithm to flag unusual behavioral patterns without human intervention.</li>
              <li><strong>Energy Forecasting:</strong> Utilizes XGBoost to predict the next 30 minutes of energy load for the house.</li>
            </ul>
            <p className="pt-2 font-medium">Use the sidebar navigation to explore the live ML visualizations.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
