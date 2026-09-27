import { createFileRoute } from "@tanstack/react-router";
import { useSmartHome } from "@/lib/smarthome/store";
import { useState, useRef, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Bot, Send, User } from "lucide-react";
import { clockTime } from "@/components/smarthome/ui-bits";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/assistant")({
  component: Assistant,
});

function Assistant() {
  const { prediction, room, plan, appliances, baselines } = useSmartHome();
  const [messages, setMessages] = useState([{ role: "ai", content: "Hi! I am your SmartHome Demo AI Assistant. I can tell you about your routine, current activity, energy usage, and anomalies based on your sensor data. How can I help?" }]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const activePlan = plan.find(p => p.status !== "COMPLETED" && p.status !== "UPCOMING");

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  const generateAIResponse = (query: string) => {
    const q = query.toLowerCase();
    let response = "I'm not sure how to answer that in demo mode. Try asking about your current activity, plan, or energy.";
    
    if (q.includes("plan") || q.includes("schedule") || q.includes("today")) {
      if (activePlan) response = `Your active plan is ${activePlan.task.task} in the ${activePlan.task.room}. Your current status is ${activePlan.status}.`;
      else response = "You don't have any active planned tasks right now.";
    } else if (q.includes("doing") || q.includes("current activity") || q.includes("now")) {
      response = `Based on ambient sensors, you appear to be ${prediction.top.activity} with ${prediction.top.probability}% confidence.`;
    } else if (q.includes("why")) {
      response = `I inferred this because: ${prediction.top.reasons.join(", ")}.`;
    } else if (q.includes("appliance") || q.includes("energy") || q.includes("on")) {
      const active = appliances.filter(a => a.on).map(a => a.name).join(", ");
      response = active ? `Currently, the following appliances are ON: ${active}.` : "All monitored appliances are currently OFF.";
    } else if (q.includes("usual") || q.includes("routine") || q.includes("exercise")) {
      const ex = baselines["Exercise"];
      if (ex) response = `Based on your history, you usually Exercise around ${clockTime(ex.typicalTime)}.`;
      else response = "I don't have enough data to determine that routine yet.";
    } else if (q.includes("save energy") || q.includes("reduce")) {
       response = "Based on your current appliance usage, you could reduce consumption by switching off appliances that remain active when their rooms are unoccupied.";
    }
    
    setTimeout(() => {
      setMessages(prev => [...prev, { role: "ai", content: response }]);
    }, 600);
  };

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;
    const msg = input.trim();
    setMessages(prev => [...prev, { role: "user", content: msg }]);
    setInput("");
    generateAIResponse(msg);
  };

  const quickQuestions = [
    "What am I doing now?",
    "Why was this activity detected?",
    "Am I following my schedule?",
    "What appliances are ON?",
    "When do I usually exercise?"
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto space-y-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2"><Bot className="size-6 text-primary"/> Demo AI Assistant</h1>
        <p className="text-muted-foreground">Context-aware chatbot powered by your local sensor data.</p>
      </div>
      
      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardContent className="flex-1 flex flex-col p-4 overflow-hidden gap-4">
          <div className="flex-1 overflow-y-auto space-y-4 p-2" ref={scrollRef}>
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-3 max-w-[80%] ${m.role === "user" ? "ml-auto flex-row-reverse" : ""}`}>
                <div className={`shrink-0 size-8 rounded-full flex items-center justify-center ${m.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                  {m.role === "user" ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className={`p-3 rounded-lg text-sm ${m.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                  {m.content}
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex flex-wrap gap-2 pt-2 border-t">
            {quickQuestions.map(q => (
               <Badge key={q} variant="secondary" className="cursor-pointer hover:bg-secondary/80" onClick={() => { setInput(q); }}>
                 {q}
               </Badge>
            ))}
          </div>
          
          <form onSubmit={handleSend} className="flex gap-2">
            <Input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask about your smart home..." className="flex-1" />
            <Button type="submit"><Send className="size-4 mr-2" /> Send</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

