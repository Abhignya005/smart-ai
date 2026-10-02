import os
BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")

pages = {
    "routine.tsx": """import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Clock, BarChart3, TrendingUp, CheckCircle, RefreshCcw, ActivitySquare, AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

export const Route = createFileRoute("/routine")({
  component: RoutineDiscovery,
});

function RoutineDiscovery() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Personal Routine Learning</h1>
            <p className="text-muted-foreground mt-2">Learn baseline habits, analyze deviations, and detect long-term drift.</p>
          </div>
          <Badge variant="outline" className="bg-green-50 text-green-700 py-1 flex gap-1 items-center">
             <RefreshCcw className="size-3"/> Baseline Updated Today
          </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Routine Score Card */}
        <Card className="lg:col-span-1 bg-primary text-primary-foreground">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-primary-foreground/80">Daily Routine Score</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center pt-4">
            <div className="relative flex items-center justify-center">
                <svg className="w-24 h-24 transform -rotate-90">
                    <circle cx="48" cy="48" r="36" stroke="currentColor" strokeWidth="8" fill="transparent" className="opacity-20" />
                    <circle cx="48" cy="48" r="36" stroke="currentColor" strokeWidth="8" fill="transparent" strokeDasharray="226" strokeDashoffset="33.9" className="text-white" />
                </svg>
                <span className="absolute text-3xl font-bold">85</span>
            </div>
            <p className="text-xs text-primary-foreground/80 mt-4 text-center">Based on completed, delayed, and unexpected activities.</p>
          </CardContent>
        </Card>
        
        {/* Typical Times */}
        <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card><CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">Typical Waking</CardTitle></CardHeader><CardContent><div className="text-xl font-bold">7:12 AM</div></CardContent></Card>
            <Card><CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">Typical Breakfast</CardTitle></CardHeader><CardContent><div className="text-xl font-bold">8:03 AM</div></CardContent></Card>
            <Card><CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">Typical Exercise</CardTitle></CardHeader><CardContent><div className="text-xl font-bold">6:00 PM</div></CardContent></Card>
            <Card><CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">Typical Sleep</CardTitle></CardHeader><CardContent><div className="text-xl font-bold">11:18 PM</div></CardContent></Card>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><TrendingUp className="size-5" /> Routine Drift Detection</CardTitle>
              <CardDescription>Detect gradual changes in a person's routine over time.</CardDescription>
            </CardHeader>
            <CardContent>
               <div className="space-y-4">
                   <div className="p-4 border rounded-md bg-muted/20">
                       <p className="font-semibold text-sm">Shift in Exercise Routine Detected</p>
                       <p className="text-xs text-muted-foreground mt-1 mb-3">Over the past 3 weeks, the start time for Evening Exercise has gradually drifted.</p>
                       <div className="flex items-center justify-between text-sm">
                           <span className="font-mono bg-background px-2 py-1 rounded border">Week 1: 18:00</span>
                           <span className="text-muted-foreground">→</span>
                           <span className="font-mono bg-background px-2 py-1 rounded border">Week 3: 18:25</span>
                       </div>
                   </div>
                   <p className="text-xs text-muted-foreground"><AlertCircle className="size-3 inline mr-1"/> Routine Adaptation Module has automatically updated the user's personal baseline to 18:25.</p>
               </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><ActivitySquare className="size-5" /> Today vs Typical Day</CardTitle>
              <CardDescription>Compare today's behavior with the learned baseline.</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    <div>
                        <div className="flex justify-between text-xs mb-1"><span>Typical Baseline (Expected)</span><span>98% Match</span></div>
                        <Progress value={98} className="h-2 bg-muted" />
                    </div>
                    <div>
                        <div className="flex justify-between text-xs mb-1"><span>Today (Observed)</span><span className="text-amber-600">85% Match</span></div>
                        <Progress value={85} className="h-2 bg-amber-100" />
                    </div>
                    <p className="text-xs text-muted-foreground pt-2">Today diverges from the typical baseline primarily during the evening hours.</p>
                </div>
            </CardContent>
          </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Planned vs Actual Analysis</CardTitle>
          <CardDescription>Compare the entered daily plan with activities detected from the dataset.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Item 1 */}
          <div className="border rounded-md p-4 bg-muted/20 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                <p className="text-xs font-medium text-muted-foreground uppercase">Expected Plan</p>
                <p className="font-bold">Breakfast (8:00 AM)</p>
            </div>
            <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                <p className="text-xs font-medium text-muted-foreground uppercase">Observed from Dataset</p>
                <p className="font-bold">Cooking & Eating (8:03 AM)</p>
            </div>
            <div className="text-center md:text-right w-full md:w-1/3">
                <Badge variant="outline" className="text-green-700 bg-green-50 border-green-200">COMPLETED</Badge>
            </div>
          </div>

          {/* Item 2 */}
          <div className="border rounded-md p-4 bg-muted/20 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                <p className="text-xs font-medium text-muted-foreground uppercase">Expected Plan</p>
                <p className="font-bold">Exercise (6:00 PM)</p>
            </div>
            <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                <p className="text-xs font-medium text-muted-foreground uppercase">Observed from Dataset</p>
                <p className="font-bold">Watching TV (6:00 PM) → Exercise (6:23 PM)</p>
            </div>
            <div className="text-center md:text-right w-full md:w-1/3">
                <Badge variant="outline" className="text-amber-600 bg-amber-50 border-amber-200">DELAYED</Badge>
            </div>
          </div>
          
          {/* Item 3 */}
          <div className="border rounded-md p-4 bg-muted/20 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                <p className="text-xs font-medium text-muted-foreground uppercase">Expected Plan</p>
                <p className="font-bold">Study (8:00 PM)</p>
            </div>
            <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                <p className="text-xs font-medium text-muted-foreground uppercase">Observed from Dataset</p>
                <p className="font-bold">Living Room Activity (8:00 PM)</p>
            </div>
            <div className="text-center md:text-right w-full md:w-1/3">
                <Badge variant="outline" className="text-orange-600 bg-orange-50 border-orange-200">TEMPORARY DEVIATION</Badge>
            </div>
          </div>
          
          {/* Item 4 */}
          <div className="border rounded-md p-4 bg-muted/20 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                <p className="text-xs font-medium text-muted-foreground uppercase">Expected Plan</p>
                <p className="font-bold">None (Free Time 2:00 PM)</p>
            </div>
            <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                <p className="text-xs font-medium text-muted-foreground uppercase">Observed from Dataset</p>
                <p className="font-bold">Sleeping / No Movement</p>
            </div>
            <div className="text-center md:text-right w-full md:w-1/3">
                <Badge variant="outline" className="text-purple-600 bg-purple-50 border-purple-200">UNEXPECTED</Badge>
            </div>
          </div>
          
          {/* Item 5 */}
          <div className="border rounded-md p-4 bg-muted/20 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                <p className="text-xs font-medium text-muted-foreground uppercase">Expected Plan</p>
                <p className="font-bold">Sleep (11:00 PM)</p>
            </div>
            <div className="space-y-1 text-center md:text-left w-full md:w-1/3">
                <p className="text-xs font-medium text-muted-foreground uppercase">Observed from Dataset</p>
                <p className="font-bold">Low Confidence Activity (42%)</p>
            </div>
            <div className="text-center md:text-right w-full md:w-1/3">
                <Badge variant="outline" className="text-slate-600 bg-slate-100 border-slate-300">NOT CONFIRMED</Badge>
            </div>
          </div>
          
        </CardContent>
      </Card>
    </div>
  );
}
""",
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
"""
}

for filename, content in pages.items():
    with open(os.path.join(ROUTES_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)
print("Step 7 completed.")

