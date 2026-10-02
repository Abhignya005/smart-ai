import os
import re

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
BACKEND_DIR = os.path.join(BASE_DIR, "ml_backend")
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

# 1. Create .env and .env.example
env_path = os.path.join(BACKEND_DIR, ".env")
env_example_path = os.path.join(BACKEND_DIR, ".env.example")
env_content = "GROQ_API_KEY=YOUR_GROQ_API_KEY\n"
if not os.path.exists(env_path):
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
with open(env_example_path, "w", encoding="utf-8") as f:
    f.write(env_content)

# 2. Update backend main.py
main_py_path = os.path.join(BACKEND_DIR, "main.py")
with open(main_py_path, "r", encoding="utf-8") as f:
    main_code = f.read()

chat_endpoint = """
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class ChatRequest(BaseModel):
    messages: list
    context: dict

@app.post("/api/chat")
async def chat_with_groq(req: ChatRequest):
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "YOUR_GROQ_API_KEY":
        return {"success": False, "error": "GROQ_API_KEY is missing or invalid in backend .env file."}
        
    try:
        client = Groq(api_key=groq_api_key)
        
        system_prompt = f\"\"\"You are the AI Assistant for a Privacy-Preserving Personal Routine & Activity Intelligence platform.
You are helping the user understand their dataset and Machine Learning results.
Do NOT invent values. ONLY use the provided context below to answer questions. If the answer isn't in the context, say "Insufficient data to determine this."
Keep answers concise, helpful, and focused on data science / ML insights.

CURRENT ML CONTEXT:
- Total Dataset Rows: {req.context.get('rows', 'Unknown')}
- Routine Consistency Score: {req.context.get('consistency', 'Unknown')}
- Current Detected Activity: {req.context.get('currentActivity', 'Unknown')} ({req.context.get('currentConf', 'Unknown')})
- Predicted Next Activity: {req.context.get('nextActivity', 'Unknown')} ({req.context.get('nextConf', 'Unknown')})
- Anomalies Detected: {req.context.get('anomalies', 'Unknown')}
- Peak Energy: {req.context.get('peakEnergy', 'Unknown')}
- Routine Drift Status: {req.context.get('driftInfo', {}).get('status', 'Unknown')} - {req.context.get('driftInfo', {}).get('text', 'Unknown')}
\"\"\"
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add user conversation history
        for msg in req.messages:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_completion_tokens=512
        )
        
        reply = completion.choices[0].message.content
        return {"success": True, "reply": reply}
    except Exception as e:
        logger.error(f"Groq API Error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
"""

if "/api/chat" not in main_code:
    # Insert before the read_root endpoint or at the bottom
    main_code = main_code.replace('if __name__ == "__main__":', chat_endpoint + '\nif __name__ == "__main__":')
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(main_code)
        
# 3. Update assistant.tsx
assistant_tsx_path = os.path.join(ROUTES_DIR, "assistant.tsx")
assistant_content = """import { createFileRoute } from "@tanstack/react-router";
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
"""
with open(assistant_tsx_path, "w", encoding="utf-8") as f:
    f.write(assistant_content)

print("Step 18 Completed: Groq API backend endpoint and React client added.")

