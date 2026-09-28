import { createFileRoute } from "@tanstack/react-router";
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
