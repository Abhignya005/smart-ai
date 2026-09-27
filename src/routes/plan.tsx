import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useSmartHome } from "@/lib/smarthome/store";
import { ACTIVITIES, ROOMS, type ScheduleTask } from "@/lib/smarthome/types";
import { SectionHeader, StatusBadge, LoadingCards } from "@/components/smarthome/ui-bits";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/plan")({
  head: () => ({
    meta: [
      { title: "Daily Plan — SmartHome AI" },
      { name: "description", content: "Create and manage your daily schedule of tasks, rooms and repeats." },
      { property: "og:title", content: "Daily Plan — SmartHome AI" },
      { property: "og:description", content: "Schedule tasks and compare them with detected activity." },
    ],
  }),
  component: PlanPage,
});

const empty = (): ScheduleTask => ({
  id: `t-${Date.now()}`,
  time: "09:00",
  task: "",
  activity: "Study",
  room: "Study",
  durationMin: 60,
  repeat: "daily",
});

function PlanPage() {
  const { ready, tasks, plan, upsertTask, deleteTask } = useSmartHome();
  const [draft, setDraft] = useState<ScheduleTask | null>(null);

  if (!ready) return <LoadingCards count={3} />;

  const save = () => {
    if (!draft) return;
    if (!draft.task.trim()) {
      toast.error("Give the task a name first.");
      return;
    }
    upsertTask(draft);
    toast.success("Task saved");
    setDraft(null);
  };

  return (
    <div className="space-y-5">
      <SectionHeader
        title="Daily Plan"
        description="Your intended routine. Detected activity is compared against it automatically."
        action={
          <Dialog open={!!draft} onOpenChange={(o) => setDraft(o ? (draft ?? empty()) : null)}>
            <DialogTrigger asChild>
              <Button onClick={() => setDraft(empty())}>
                <Plus className="size-4" /> Add task
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>{tasks.some((t) => t.id === draft?.id) ? "Edit task" : "New task"}</DialogTitle>
              </DialogHeader>
              {draft && (
                <div className="grid gap-3">
                  <div className="grid gap-1.5">
                    <Label htmlFor="task">Task</Label>
                    <Input
                      id="task"
                      value={draft.task}
                      placeholder="e.g. Breakfast"
                      onChange={(e) => setDraft({ ...draft, task: e.target.value })}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="grid gap-1.5">
                      <Label htmlFor="time">Time</Label>
                      <Input
                        id="time"
                        type="time"
                        value={draft.time}
                        onChange={(e) => setDraft({ ...draft, time: e.target.value })}
                      />
                    </div>
                    <div className="grid gap-1.5">
                      <Label htmlFor="dur">Duration (min)</Label>
                      <Input
                        id="dur"
                        type="number"
                        min={5}
                        value={draft.durationMin}
                        onChange={(e) => setDraft({ ...draft, durationMin: Number(e.target.value) })}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="grid gap-1.5">
                      <Label>Activity</Label>
                      <Select
                        value={draft.activity}
                        onValueChange={(v) => setDraft({ ...draft, activity: v as ScheduleTask["activity"] })}
                      >
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                          {ACTIVITIES.map((a) => (
                            <SelectItem key={a} value={a}>{a}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid gap-1.5">
                      <Label>Expected room</Label>
                      <Select
                        value={draft.room}
                        onValueChange={(v) => setDraft({ ...draft, room: v as ScheduleTask["room"] })}
                      >
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                          {ROOMS.map((r) => (
                            <SelectItem key={r} value={r}>{r}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid gap-1.5">
                    <Label>Repeat</Label>
                    <Select
                      value={draft.repeat}
                      onValueChange={(v) => setDraft({ ...draft, repeat: v as ScheduleTask["repeat"] })}
                    >
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="daily">Every day</SelectItem>
                        <SelectItem value="weekdays">Weekdays</SelectItem>
                        <SelectItem value="weekends">Weekends</SelectItem>
                        <SelectItem value="once">Once</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}
              <DialogFooter>
                <Button variant="outline" onClick={() => setDraft(null)}>Cancel</Button>
                <Button onClick={save}>Save task</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      {plan.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-sm text-muted-foreground">
            No tasks yet. Add your first one to start comparing plan with detected activity.
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Timeline</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {plan.map((p) => (
              <div
                key={p.task.id}
                className="flex flex-wrap items-center gap-3 rounded-lg border p-3 sm:flex-nowrap"
              >
                <div className="w-16 shrink-0 text-sm font-semibold tabular-nums">{p.task.time}</div>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{p.task.task}</p>
                  <p className="text-xs text-muted-foreground">
                    {p.task.activity} · {p.task.room} · {p.task.durationMin} min · {p.task.repeat}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">{p.explanation}</p>
                </div>
                <StatusBadge status={p.status} />
                <div className="flex gap-1">
                  <Button size="icon" variant="ghost" aria-label="Edit task" onClick={() => setDraft(p.task)}>
                    <Pencil className="size-4" />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    aria-label="Delete task"
                    onClick={() => {
                      deleteTask(p.task.id);
                      toast("Task removed");
                    }}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
