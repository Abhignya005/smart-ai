import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, User, Send, Database, Loader2, AlertTriangle } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { loadDataset } from "@/lib/datasetUtils";
import { calculateDashboardMetrics } from "@/lib/mlUtils";

export const Route = createFileRoute("/assistant")({
  component: SmartHomeAIAnalyst,
});

function SmartHomeAIAnalyst() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loadingContext, setLoadingContext] = useState(true);
  
  useEffect(() => {
      const dataset = loadDataset();
      if (dataset) setMetrics(calculateDashboardMetrics(dataset));
      setLoadingContext(false);
  }, []);

  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am connected to your uploaded dataset and ML models via the Groq API. Ask me about activities, plans, or predictions.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !metrics || isLoading) return;
    const userMsg = input.trim();
    const newMessages = [...messages, { role: 'user', content: userMsg }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);
    setApiError(null);
    
    try {
        const response = await fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: newMessages.map(m => ({ role: m.role, content: m.content })),
                context: metrics
            })
        });
        
        const data = await response.json();
        if (data.success) {
            setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
        } else {
            setApiError(data.error || "Failed to communicate with Groq API.");
        }
    } catch (err: any) {
        setApiError("Backend connection failed. Make sure the FastAPI server is running.");
    } finally {
        setIsLoading(false);
    }
  };

  if (loadingContext) return <div className="p-8 text-center flex flex-col items-center"><Loader2 className="mx-auto size-12 mb-4 animate-spin"/>Loading ML Context...</div>;
  if (!metrics) return <div className="p-8 text-center"><Database className="mx-auto size-12 opacity-50 mb-4"/>Upload dataset first in the Data Ingestion tab.</div>;

  return (
    <div className="space-y-6 h-[80vh] flex flex-col">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2"><Bot className="size-8 text-primary"/> AI Assistant (Powered by Groq)</h1>
        <p className="text-muted-foreground mt-2">Securely querying {metrics.rows} records via backend API.</p>
      </div>

      <Card className="flex-1 flex flex-col min-h-0">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
             <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && <div className="bg-primary/10 p-2 rounded-full h-fit"><Bot className="size-4 text-primary" /></div>}
                <div className={`p-3 rounded-lg text-sm max-w-[80%] ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted whitespace-pre-wrap'}`}>
                    {msg.content}
                </div>
                {msg.role === 'user' && <div className="bg-muted p-2 rounded-full h-fit"><User className="size-4" /></div>}
             </div>
          ))}
          
          {isLoading && (
              <div className="flex gap-3 justify-start">
                  <div className="bg-primary/10 p-2 rounded-full h-fit"><Bot className="size-4 text-primary" /></div>
                  <div className="p-3 rounded-lg text-sm bg-muted flex items-center gap-2">
                      <Loader2 className="size-4 animate-spin" /> Thinking...
                  </div>
              </div>
          )}
          
          {apiError && (
              <div className="flex gap-3 justify-center">
                  <div className="p-3 rounded-lg text-sm bg-red-50 text-red-700 flex items-center gap-2 border border-red-200">
                      <AlertTriangle className="size-4" /> {apiError}
                  </div>
              </div>
          )}
          <div ref={messagesEndRef} />
        </CardContent>
        <CardFooter className="p-4 border-t">
          <form className="flex w-full gap-2" onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
             <Input placeholder="Ask about your routine, anomalies, or predictions..." value={input} onChange={e => setInput(e.target.value)} disabled={isLoading} />
             <Button type="submit" disabled={isLoading || !input.trim()}><Send className="size-4" /></Button>
          </form>
        </CardFooter>
      </Card>
    </div>
  );
}
