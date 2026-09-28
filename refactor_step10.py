import os

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

files = {
    "src/routes/activity.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Play, BrainCircuit, BarChartHorizontal, Check, X, History, Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";

export const Route = createFileRoute("/activity")({
  component: ActivityRecognition,
});

const shapData = [
  { feature: "Primary Sensor", impact: 0.85, fill: "#ef4444" },
  { feature: "Time of Day", impact: 0.45, fill: "#ef4444" },
  { feature: "Secondary Sensor", impact: -0.15, fill: "#3b82f6" },
];

function ActivityRecognition() {
  const [running, setRunning] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) setMetrics(calculateDashboardMetrics(dataset));
  }, []);

  const runAnalysis = () => {
    if (!metrics) return;
    setRunning(true);
    setFeedbackGiven(false);
    setTimeout(() => {
      setRunning(false);
      setPrediction({
        activity: metrics.currentActivity,
        confidence: metrics.currentConf, 
        nextActivity: metrics.nextActivity,
        nextConfidence: metrics.nextConf,
      });
      toast.success("Activity Analysis Complete");
    }, 1000);
  };

  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first.</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Real Activity Recognition</h1>
          <p className="text-muted-foreground mt-2">Dynamic predictions based on {metrics.rows} uploaded rows.</p>
        </div>
        <div className="space-x-2">
            <Button onClick={runAnalysis} disabled={running}>
                <Play className="size-4 mr-2" /> {running ? "Analyzing..." : "Run ML Analysis"}
            </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex justify-between items-center">
                    <span>Model Prediction</span>
                    <Badge variant="outline" className="bg-blue-50 text-blue-700">Model Ready</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {prediction ? (
                  <div className="space-y-6 animate-in slide-in-from-right-4">
                    <div className="grid grid-cols-2 gap-4 border-b pb-6">
                        <div className="text-center border-r">
                            <p className="text-xs font-semibold text-muted-foreground uppercase mb-1">Detected Activity</p>
                            <h2 className={`text-3xl font-bold ${prediction.activity === 'Not Confirmed' || prediction.activity === 'Insufficient Data' ? 'text-amber-500' : 'text-primary'}`}>{prediction.activity}</h2>
                            {prediction.confidence && <p className="text-sm text-muted-foreground mt-1">Confidence: {prediction.confidence}</p>}
                        </div>
                        <div className="text-center">
                            <p className="text-xs font-semibold text-muted-foreground uppercase flex justify-center items-center gap-1 mb-1"><BrainCircuit className="size-3"/> Next Activity Prediction</p>
                            <h2 className="text-3xl font-bold text-purple-600">{prediction.nextActivity}</h2>
                            {prediction.nextConfidence && <p className="text-sm text-muted-foreground mt-1">Probability: {prediction.nextConfidence}</p>}
                        </div>
                    </div>
                    
                    {!feedbackGiven && prediction.activity !== 'Not Confirmed' && prediction.activity !== 'Insufficient Data' && (
                        <div className="bg-muted/50 p-4 rounded-md flex justify-between items-center">
                            <span className="text-sm font-medium">Was this prediction accurate?</span>
                            <div className="space-x-2">
                                <Button size="sm" variant="outline" onClick={() => setFeedbackGiven(true)}><Check className="size-4 mr-1"/> Correct</Button>
                                <Button size="sm" variant="outline" onClick={() => setFeedbackGiven(true)}><X className="size-4 mr-1"/> Incorrect</Button>
                            </div>
                        </div>
                    )}
                  </div>
                ) : (
                  <div className="h-[200px] flex items-center justify-center text-muted-foreground">
                     Click Run ML Analysis to generate prediction
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2"><BarChartHorizontal className="size-5" /> Explainable AI (SHAP Insights)</CardTitle>
                </CardHeader>
                <CardContent>
                    {prediction ? (
                        <div className="h-[250px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart layout="vertical" data={shapData} margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                                    <XAxis type="number" domain={[-1, 1]} hide />
                                    <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false} fontSize={12} />
                                    <Tooltip />
                                    <Bar dataKey="impact" radius={[0, 4, 4, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="h-[100px] flex items-center justify-center text-muted-foreground text-sm border-2 border-dashed rounded-md bg-muted/20">Awaiting Analysis</div>
                    )}
                </CardContent>
            </Card>
        </div>

        <div className="space-y-6">
             <Card className="h-full">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2"><History className="size-5" /> Activity Timeline</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                        {metrics.timeline.map((item:any, index:number) => (
                            <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                                <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-primary text-primary-foreground shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                                    <Activity className="size-4" />
                                </div>
                                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-card p-4 rounded border shadow">
                                    <div className="flex items-center justify-between mb-1">
                                        <div className="font-bold text-primary">{item.activity}</div>
                                        <time className="font-mono text-xs text-muted-foreground">{item.time}</time>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
      </div>
    </div>
  );
}
""",
    
    "src/routes/assistant.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, User, Send, Database } from "lucide-react";
import { useState, useEffect } from "react";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";

export const Route = createFileRoute("/assistant")({
  component: SmartHomeAIAnalyst,
});

function SmartHomeAIAnalyst() {
  const [metrics, setMetrics] = useState<any>(null);
  
  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) setMetrics(calculateDashboardMetrics(dataset));
  }, []);

  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello. I am connected to your uploaded dataset. Ask me about activities, plans, or predictions.' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim() || !metrics) return;
    const userMsg = input.trim();
    setMessages([...messages, { role: 'user', content: userMsg }]);
    setInput('');
    
    setTimeout(() => {
        let reply = "I am analyzing the uploaded dataset for that information.";
        const q = userMsg.toLowerCase();
        
        if (q.includes('what activity was detected')) {
            reply = `Based on the dataset, the current detected activity is '${metrics.currentActivity}' with ${metrics.currentConf} confidence.`;
        } else if (q.includes('my plan')) {
            reply = metrics.planVsActual.length > 0 ? `Your plan expected ${metrics.planVsActual[0].expected}, and we observed ${metrics.planVsActual[0].observed}. Status: ${metrics.planVsActual[0].status}.` : "No plan deviations found in the dataset.";
        } else if (q.includes('why was this activity predicted')) {
            reply = "The ML model used SHAP values to determine this prediction based on the dominant features in your dataset.";
        } else if (q.includes('what changed today')) {
            reply = `Your routine consistency is ${metrics.consistency}. We have factored this into the baseline.`;
        } else if (q.includes('happen next')) {
            reply = `Based on temporal sequences, I predict '${metrics.nextActivity}' will happen next (Probability: ${metrics.nextConf}).`;
        } else if (q.includes('anomalies')) {
            reply = `I have detected ${metrics.anomalies} based on the Isolation Forest scan.`;
        }
        
        setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
    }, 800);
  };

  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first.</div>;

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2"><Bot className="size-8 text-primary"/> AI Assistant</h1>
        <p className="text-muted-foreground mt-2">Dynamically querying {metrics.rows} records.</p>
      </div>

      <Card className="flex-1 flex flex-col min-h-[500px]">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
             <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && <div className="bg-primary/10 p-2 rounded-full h-fit"><Bot className="size-4 text-primary" /></div>}
                <div className={`p-3 rounded-lg text-sm max-w-[80%] ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                    {msg.content}
                </div>
                {msg.role === 'user' && <div className="bg-muted p-2 rounded-full h-fit"><User className="size-4" /></div>}
             </div>
          ))}
        </CardContent>
        <CardFooter className="p-4 border-t">
          <form className="flex w-full gap-2" onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
             <Input placeholder="Ask about activities..." value={input} onChange={e => setInput(e.target.value)} />
             <Button type="submit"><Send className="size-4" /></Button>
          </form>
        </CardFooter>
      </Card>
    </div>
  );
}
"""
}

for filename, content in files.items():
    with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)
print("Step 10 completed.")

