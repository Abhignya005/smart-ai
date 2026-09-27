import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export const Route = createFileRoute('/models')({
  component: ModelsComponent,
})

function ModelsComponent() {
  const [metrics, setMetrics] = useState<any>(null)
  
  useEffect(() => {
    fetch('http://localhost:8000/api/metrics')
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(err => console.error(err))
  }, [])

  if (!metrics) return <div className="p-8">Loading ML Metrics from Backend...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Model Comparison & Metrics</h1>
        <p className="text-muted-foreground mt-2">Real performance metrics loaded from the Python ML Backend.</p>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Activity Recognition (Classification)</CardTitle>
            <CardDescription>Predicting user activity from ambient sensors.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(metrics.Activity_Recognition).map(([modelName, scores]: any) => (
              <div key={modelName} className="rounded-lg border p-4 space-y-2">
                <div className="font-semibold">{modelName} {modelName === 'Random Forest' && <Badge className="ml-2">Deployed</Badge>}</div>
                <div className="grid grid-cols-2 text-sm gap-2">
                  <div>Accuracy: <span className="font-medium text-primary">{(scores.Accuracy * 100).toFixed(1)}%</span></div>
                  <div>F1 Score: <span className="font-medium text-primary">{(scores.F1_Weighted * 100).toFixed(1)}%</span></div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Energy Forecasting (Regression)</CardTitle>
            <CardDescription>Predicting future household power consumption.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(metrics.Energy_Forecasting).map(([modelName, scores]: any) => (
              <div key={modelName} className="rounded-lg border p-4 space-y-2">
                <div className="font-semibold">{modelName} {modelName === 'XGBoost' && <Badge className="ml-2">Deployed</Badge>}</div>
                <div className="grid grid-cols-2 text-sm gap-2">
                  <div>MAE: <span className="font-medium text-primary">{scores.MAE} kW</span></div>
                  <div>RMSE: <span className="font-medium text-primary">{scores.RMSE} kW</span></div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Random Forest Feature Importance</CardTitle>
            <CardDescription>What sensors matter most for activity recognition?</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(metrics.Feature_Importance)
                .sort(([,a]: any, [,b]: any) => b - a)
                .map(([feature, importance]: any) => (
                <div key={feature}>
                  <div className="flex justify-between text-sm mb-1">
                    <span>{feature}</span>
                    <span className="font-medium text-muted-foreground">{importance}</span>
                  </div>
                  <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary" 
                      style={{ width: `${importance * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

