import os
BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

pages = {
    "assistant.tsx": """import { createFileRoute } from "@tanstack/react-router";
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
    { role: 'assistant', content: 'Hello. I am the Smart Home AI Analyst. I have context on the 125,430 rows of your current dataset. You can ask me about activities, anomalies, or energy trends.' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages([...messages, { role: 'user', content: userMsg }]);
    setInput('');
    
    // Contextual Demo Responses
    setTimeout(() => {
        let reply = "Based on the analyzed dataset, I'm analyzing that pattern now.";
        if (userMsg.toLowerCase().includes('highest energy')) {
            reply = "Based on the analyzed dataset, the AC accounts for the highest observed energy consumption.";
        } else if (userMsg.toLowerCase().includes('when does') && userMsg.toLowerCase().includes('energy')) {
            reply = "The highest consumption typically occurs during the evening period (18:00 - 22:00).";
        } else if (userMsg.toLowerCase().includes('unusual')) {
            reply = "An unusual appliance event was detected at 3:12 AM, outside the appliance's normal usage period (Anomaly Score: -0.84).";
        } else if (userMsg.toLowerCase().includes('dinner')) {
            reply = "The discovered routine indicates dinner usually begins around 8:14 PM.";
        } else if (userMsg.toLowerCase().includes('recommend')) {
            reply = "I recommend shifting heavy appliance usage (like Laundry) to off-peak hours (10 PM - 6 AM) to reduce your peak load footprint.";
        }
        setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
    }, 1000);
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2"><Bot className="size-8 text-primary"/> Smart Home AI Analyst</h1>
        <p className="text-muted-foreground mt-2">Natural-language exploration of household data (Context-Aware Demo AI Assistant).</p>
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
             <Input placeholder="Ask about anomalies, routines, or energy..." value={input} onChange={e => setInput(e.target.value)} />
             <Button type="submit"><Send className="size-4" /></Button>
          </form>
        </CardFooter>
      </Card>
    </div>
  );
}
""",
    "settings.tsx": """import { createFileRoute } from "@tanstack/react-router";
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
"""
}

for filename, content in pages.items():
    with open(os.path.join(ROUTES_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)
print("Step 5 completed.")

