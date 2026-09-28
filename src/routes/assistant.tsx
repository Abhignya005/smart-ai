import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, User, Send } from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/assistant")({
  component: SmartHomeAIAnalyst,
});

function SmartHomeAIAnalyst() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello. I am the Smart Home AI Analyst. I have full context on the uploaded dataset and ML results. Ask me about activities, your plan, predictions, or routines.' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages([...messages, { role: 'user', content: userMsg }]);
    setInput('');
    
    // Contextual Demo Responses mapping to specific user requirements
    setTimeout(() => {
        let reply = "Based on the recent telemetry, there is active motion and power consumption occurring. Would you like me to run a deeper behavioral analysis on this period?";
        
        const q = userMsg.toLowerCase();
        
        if (q.includes('what activity was detected')) {
            reply = "Based on the dataset, the current detected activity is 'Cooking' with a 91% confidence score.";
        } else if (q.includes('following my plan') || q.includes('my plan')) {
            reply = "You are currently experiencing a 'Delayed' status. Your plan expected 'Exercise' at 6:00 PM, but the dataset observed 'Watching TV' followed by Exercise at 6:23 PM.";
        } else if (q.includes('why was this activity predicted') || q.includes('why')) {
            reply = "The Random Forest model predicted 'Cooking' primarily because of high 'Oven Power' (SHAP +0.85) and active 'Kitchen Motion' (SHAP +0.65).";
        } else if (q.includes('what changed today') || q.includes('changed today')) {
            reply = "Today diverges from your typical baseline primarily during the evening. We detected a Routine Drift where your exercise time has shifted by 25 minutes compared to your learned baseline.";
        } else if (q.includes('usually do at this time') || q.includes('usually do')) {
            reply = "At 18:00 (6:00 PM), the historical dataset shows you typically Exercise.";
        } else if (q.includes('what will probably happen next') || q.includes('happen next')) {
            reply = "Based on temporal patterns and your previous activities today, the Next Activity Prediction model estimates 'Eating' will happen next with a 78% probability.";
        } else if (q.includes('how many devices') || q.includes('how many appliances')) {
            reply = "Currently, there are 3 active devices drawing power: The AC (1.2 kW), the TV (0.13 kW), and the Refrigerator (0.15 kW).";
        } else if (q.includes('living room') || q.includes('is the person')) {
            reply = "Yes, based on the sensor fusion, there is active motion in the Living Room and the TV is drawing power, indicating human presence with 91% confidence.";
        } 
        
        setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
    }, 1000);
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2"><Bot className="size-8 text-primary"/> AI Assistant</h1>
        <p className="text-muted-foreground mt-2">Connects to the uploaded dataset and ML results for conversational analytics.</p>
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
             <Input placeholder="Try: 'What activity was detected?' or 'Am I following my plan?'" value={input} onChange={e => setInput(e.target.value)} />
             <Button type="submit"><Send className="size-4" /></Button>
          </form>
        </CardFooter>
      </Card>
    </div>
  );
}
