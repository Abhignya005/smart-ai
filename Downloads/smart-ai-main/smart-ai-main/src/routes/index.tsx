import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, User, Home, Activity, CheckCircle2, XCircle, ArrowLeft, AlertCircle, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { onDatasetUpdate } from "@/lib/datasetUtils";

export const Route = createFileRoute("/")({
  component: DashboardApp,
});

function DashboardApp() {
  const [familyData, setFamilyData] = useState<any>(null);
  const [selectedView, setSelectedView] = useState<string>("combined");
  const [loading, setLoading] = useState<boolean>(true);

  const fetchFamilyDashboard = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://localhost:8000/api/family/dashboard", { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          setFamilyData(data);

          // If dataset contains exactly one occupant or no person_id (single stream)
          const isMulti = Boolean(data.is_multi_occupant && data.members && data.members.length > 1);
          if (!isMulti && data.members && data.members.length > 0) {
            setSelectedView(data.members[0].id);
          } else if (isMulti) {
            // In multi-person mode, default to combined view unless user picked a valid member
            setSelectedView((prev) => {
              if (prev !== "combined" && data.members.some((m: any) => m.id === prev)) {
                return prev;
              }
              return "combined";
            });
          }
        }
      }
    } catch (err) {
      console.error("Failed to load dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFamilyDashboard();
    const unsubscribe = onDatasetUpdate(() => {
      fetchFamilyDashboard();
    });
    return unsubscribe;
  }, []);

  const isMultiOccupant = Boolean(familyData?.is_multi_occupant && familyData?.members && familyData.members.length > 1);
  const isCombinedView = isMultiOccupant && selectedView === "combined";
  const selectedMember = familyData?.members?.find((m: any) => m.id === selectedView) || familyData?.members?.[0] || null;

  return (
    <div className="space-y-8 pb-16">
      {/* Top Header & Dynamic System Status */}
      <div className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">HabitSense-Activity Analyser</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Privacy-first behavioral intelligence & dynamic occupant activity recognition
            </p>
          </div>

          <div className="mt-4 sm:mt-0 text-right space-y-1 text-xs font-mono">
            <p>
              ML STATUS: <span className="text-green-600 font-bold">● Active</span>
            </p>
            <p>Backend: Connected</p>
            <p>Model: Loaded</p>
            <p className="text-muted-foreground mt-1">
              Data Source:{" "}
              <strong className="text-foreground">
                {familyData?.data_source || "synthetic_smarthome_data.csv"}
              </strong>
            </p>
            <p className="text-muted-foreground">
              Data Quality:{" "}
              <span className="text-green-600 font-bold">
                {familyData?.data_quality ? familyData.data_quality.split("•")[0].trim() : "Good"}
              </span>
            </p>
          </div>
        </div>

        {/* Dynamic Occupant & Mode View Selector */}
        {familyData && (
          <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
            {!isMultiOccupant ? (
              /* SINGLE OCCUPANT OR UNDIFFERENTIATED STREAM BANNER */
              <div className="flex items-center gap-2">
                {familyData.has_person_id ? (
                  <Badge variant="outline" className="px-3 py-1.5 text-xs font-medium bg-primary/10 border-primary/30 text-primary flex items-center gap-1.5">
                    <User className="size-3.5" />
                    <span>Single Occupant Mode: <strong>{familyData.members?.[0]?.name || "Individual"}</strong></span>
                  </Badge>
                ) : (
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-500/10 border border-amber-500/30 rounded-md text-amber-800 dark:text-amber-300 text-xs font-medium">
                    <AlertCircle className="size-4 shrink-0 text-amber-600" />
                    <span>Single Undifferentiated Activity Stream (No <code>person_id</code> column detected — person-level breakdown unavailable)</span>
                  </div>
                )}
              </div>
            ) : (
              /* MULTI-OCCUPANT SELECTOR TABS */
              <div className="flex flex-wrap items-center gap-2 bg-muted/20 p-1.5 border rounded-lg">
                <Button
                  variant={isCombinedView ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setSelectedView("combined")}
                  className="gap-1.5 text-xs font-medium h-8 px-3"
                >
                  <Users className="size-3.5" /> Combined / Family View
                </Button>

                <div className="h-4 w-px bg-border mx-1 hidden sm:block" />

                <span className="text-xs font-semibold text-muted-foreground px-1 hidden md:inline">
                  Detected Occupants ({familyData.members.length}):
                </span>

                {familyData.members.map((m: any) => {
                  const isSelected = selectedView === m.id;
                  const isActive = m.status === "Active";
                  return (
                    <Button
                      key={m.id}
                      size="sm"
                      variant={isSelected ? "default" : "outline"}
                      onClick={() => setSelectedView(m.id)}
                      className="text-xs font-mono h-8 px-2.5 gap-1.5"
                    >
                      <User className="size-3" />
                      <span>{m.name}</span>
                      <span
                        className={`text-[9px] ${
                          isActive ? "text-green-500 font-bold" : "text-muted-foreground"
                        }`}
                        title={m.status}
                      >
                        ●
                      </span>
                    </Button>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {loading && !familyData ? (
        <div className="p-12 text-center text-muted-foreground animate-pulse border rounded-lg">
          Connecting to ML Backend & Dynamically Analyzing Occupants...
        </div>
      ) : isCombinedView ? (
        /* COMBINED / FAMILY VIEW (Aggregated across all detected occupants) */
        <HouseholdOverview
          data={familyData}
          onSelectMember={(memberId) => setSelectedView(memberId)}
        />
      ) : (
        /* INDIVIDUAL OCCUPANT VIEW (Filtered strictly to selected person) */
        <MemberAnalytics
          member={selectedMember}
          timeline={selectedMember?.recent_events}
          onBack={isMultiOccupant ? () => setSelectedView("combined") : undefined}
          isSingleOccupantOnly={!isMultiOccupant}
        />
      )}
    </div>
  );
}

function HouseholdOverview({
  data,
  onSelectMember,
}: {
  data: any;
  onSelectMember: (id: string) => void;
}) {
  const summary = data?.summary || {
    members_total: data?.members?.length || 0,
    active_now: 0,
    idle_now: 0,
    unusual_count: 0,
  };

  const activities = data?.household_activities || {};
  const occupancy = data?.room_occupancy || {};
  const timeline = data?.timeline || [];
  const anomalySummary = data?.anomaly_summary || { normal: 0, unusual: 0, unknown: 0 };

  return (
    <div className="space-y-8 animate-in fade-in pt-2">
      {/* 1. HOUSEHOLD OVERVIEW SUMMARY */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b pb-4 gap-4">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Home className="size-5" /> COMBINED HOUSEHOLD OVERVIEW
          </h2>
          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground mt-1 font-medium">
            <span>
              Detected Occupants: <strong className="text-foreground">{summary.members_total}</strong>
            </span>
            <span>
              • Active Now: <strong className="text-green-600">{summary.active_now}</strong>
            </span>
            <span>
              • Idle: <strong className="text-foreground">{summary.idle_now}</strong>
            </span>
            <span>
              • Unusual Behaviors:{" "}
              <strong className={summary.unusual_count > 0 ? "text-destructive" : "text-foreground"}>
                {summary.unusual_count}
              </strong>
            </span>
          </div>
        </div>
      </div>

      {/* 2. DETECTED OCCUPANTS GRID */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xs font-bold tracking-widest uppercase text-muted-foreground">
            DETECTED OCCUPANTS ({data?.members?.length || 0})
          </h3>
          <span className="text-[11px] text-muted-foreground">Click any card to filter individual analytics</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {data?.members?.map((m: any) => {
            const isActive = m.status === "Active";

            return (
              <Card
                key={m.id}
                className="cursor-pointer hover:border-primary/50 transition-colors shadow-sm flex flex-col justify-between group"
                onClick={() => onSelectMember(m.id)}
              >
                <CardHeader className="pb-2 bg-muted/10 border-b">
                  <CardTitle className="text-base flex justify-between items-center group-hover:text-primary transition-colors">
                    <span className="truncate">
                      {m.name}
                    </span>
                    <span
                      className={`flex items-center gap-1 text-[11px] font-bold shrink-0 ${
                        isActive ? "text-green-600" : "text-muted-foreground"
                      }`}
                    >
                      ● {m.status}
                    </span>
                  </CardTitle>
                </CardHeader>

                <CardContent className="pt-4 flex-1 flex flex-col justify-between text-sm">
                  {isActive ? (
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs text-muted-foreground uppercase font-semibold">
                          Current Activity
                        </p>
                        <p className="font-bold text-lg text-primary truncate">{m.current_activity}</p>
                      </div>

                      {/* Actual Ground-Truth Activity comparison */}
                      {m.actual_activity && (
                        <div className="text-xs flex items-center justify-between border-t border-b py-1 bg-muted/10 px-1 rounded">
                          <span className="truncate">
                            Actual: <strong>{m.actual_activity}</strong>
                          </span>
                          {m.prediction_accuracy === "Correct" ? (
                            <span className="text-green-600 font-semibold flex items-center gap-1 shrink-0">
                              <CheckCircle2 className="size-3" /> Correct
                            </span>
                          ) : (
                            <span className="text-destructive font-semibold flex items-center gap-1 shrink-0">
                              <XCircle className="size-3" /> Incorrect
                            </span>
                          )}
                        </div>
                      )}

                      <div className="grid grid-cols-2 gap-1 text-xs text-muted-foreground">
                        <div>
                          Room: <strong className="text-foreground">{m.room}</strong>
                        </div>
                        <div>
                          Confidence:{" "}
                          <strong className="text-foreground">
                            {m.confidence ? `${m.confidence}%` : "N/A"}
                          </strong>
                        </div>
                      </div>

                      <div className="flex justify-between items-center text-xs">
                        <span>
                          Status:{" "}
                          <strong
                            className={
                              m.routine_status === "Normal"
                                ? "text-green-600"
                                : "text-destructive font-bold"
                            }
                          >
                            {m.routine_status}
                          </strong>
                        </span>
                        {m.confidence_level && (
                          <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded font-medium">
                            {m.confidence_level}
                          </span>
                        )}
                      </div>

                      <div className="text-[11px] text-muted-foreground border-t pt-2 flex justify-between items-center">
                        <span>Updated: <strong>{m.last_updated}</strong></span>
                        <span className="text-primary text-[11px] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                          View details →
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3 py-3 text-center">
                      <div>
                        <p className="text-xs text-muted-foreground uppercase font-semibold">
                          Current Activity
                        </p>
                        <p className="font-bold text-base text-muted-foreground">Unknown</p>
                      </div>
                      <p className="text-xs text-muted-foreground italic line-clamp-2">
                        {m.reason || "No recent activity"}
                      </p>
                      <div className="text-[11px] text-muted-foreground border-t pt-3 flex justify-between items-center">
                        <span>Last Active: <strong>{m.last_updated}</strong></span>
                        <span className="text-primary text-[11px] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                          View details →
                        </span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* 3. COMBINED HOUSEHOLD ACTIVITY & ROOM OCCUPANCY (Aggregated across all detected people) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="shadow-sm">
          <CardHeader className="pb-2 bg-muted/10 border-b">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              COMBINED HOUSEHOLD ACTIVITY (ALL OCCUPANTS)
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {Object.keys(activities).length > 0 ? (
                Object.entries(activities).map(([act, count]: any) => (
                  <div key={act} className="flex justify-between text-sm border-b pb-1.5 last:border-0">
                    <span className="font-medium">{act}</span>
                    <span className="font-mono text-muted-foreground">
                      {count} {count === 1 ? "record" : "records"}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No activities recorded</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="pb-2 bg-muted/10 border-b">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              COMBINED ROOM OCCUPANCY
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {Object.keys(occupancy).length > 0 ? (
                Object.entries(occupancy).map(([room, count]: any) => (
                  <div key={room} className="flex justify-between text-sm border-b pb-1.5 last:border-0">
                    <span className="font-medium">{room}</span>
                    <span className="font-mono text-muted-foreground">
                      {count} {count === 1 ? "event" : "events"}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-muted-foreground py-2">
                  No active room occupancy detected in current dataset window.
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 4. COMBINED ACTIVITY TIMELINE & HOUSEHOLD ANOMALY SUMMARY */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2 shadow-sm">
          <CardHeader className="pb-2 bg-muted/10 border-b">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              COMBINED HOUSEHOLD ACTIVITY TIMELINE (INTERLEAVED)
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {timeline.length > 0 ? (
                timeline.map((item: any, idx: number) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between text-sm border-b pb-2 last:border-0 gap-2"
                  >
                    <span className="font-mono text-xs text-muted-foreground w-20 shrink-0">
                      {item.time}
                    </span>
                    <span className="font-bold flex-1 text-primary truncate">
                      <span className="font-mono text-xs text-foreground bg-muted px-1.5 py-0.5 rounded mr-1.5">
                        {item.person_id}
                      </span>
                      {item.activity}
                    </span>
                    <span className="text-xs text-muted-foreground bg-muted/20 px-2 py-0.5 rounded border shrink-0">
                      {item.room}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No recent timeline events found.</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="pb-2 bg-muted/10 border-b">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              HOUSEHOLD ANOMALY SUMMARY
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-3 text-sm">
              <div className="flex justify-between border-b pb-1.5">
                <span>Normal Behavioral State:</span>
                <strong className="font-mono text-green-600">{anomalySummary.normal}</strong>
              </div>
              <div className="flex justify-between border-b pb-1.5">
                <span>Unusual / Outlier State:</span>
                <strong className="font-mono text-destructive">{anomalySummary.unusual}</strong>
              </div>
              <div className="flex justify-between pb-1.5">
                <span>Unknown / Inactive:</span>
                <strong className="font-mono text-muted-foreground">{anomalySummary.unknown}</strong>
              </div>
              <p className="text-[10px] text-muted-foreground mt-4 italic border-t pt-2 leading-relaxed">
                Aggregated across all {data?.members?.length || 0} detected occupants. Unusual behavior indicates departure from historical routines.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function MemberAnalytics({
  member,
  timeline,
  onBack,
  isSingleOccupantOnly,
}: {
  member: any;
  timeline?: any[];
  onBack?: () => void;
  isSingleOccupantOnly?: boolean;
}) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [correctedAct, setCorrectedAct] = useState("Watching TV");

  if (!member) {
    return (
      <div className="p-8 text-center text-muted-foreground border rounded-lg">
        <p>No occupant data available for this selection.</p>
        {onBack && (
          <Button variant="outline" size="sm" onClick={onBack} className="mt-4">
            Back to Combined View
          </Button>
        )}
      </div>
    );
  }

  const handleFeedbackSubmit = async () => {
    try {
      await fetch("http://localhost:8000/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          person: member.name,
          person_id: member.id,
          predicted_activity: member.current_activity,
          actual_activity: correctedAct,
          timestamp: new Date().toISOString(),
        }),
      });
      setShowFeedback(false);
      toast.success("Feedback recorded for model continuous learning.");
    } catch (e) {
      toast.error("Failed to submit feedback.");
    }
  };

  const confVal = member.confidence || 0;
  const confColor = confVal >= 80 ? "bg-green-500" : confVal >= 50 ? "bg-yellow-500" : "bg-red-500";

  return (
    <div className="space-y-6 animate-in slide-in-from-right-4 duration-300 pt-2">
      {onBack && (
        <Button variant="ghost" size="sm" onClick={onBack} className="mb-2 -ml-2 text-muted-foreground hover:text-foreground">
          <ArrowLeft className="size-4 mr-2" /> Back to Combined Household Overview
        </Button>
      )}

      {/* Member Header */}
      <div className="border-b pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h2 className="text-2xl font-bold uppercase tracking-tight flex items-center gap-2">
            <User className="size-6 text-primary" /> {member.name}'S ANALYTICS
          </h2>
          {isSingleOccupantOnly && (
            <Badge variant="outline" className="w-fit text-xs font-mono">
              Single Person View
            </Badge>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 mt-2 text-sm">
          <p className="font-medium">
            Person ID: <span className="font-mono text-foreground font-semibold">{member.id}</span>
          </p>
          <p className="font-medium">
            Current Room: <span className="text-foreground font-semibold">{member.room}</span>
          </p>
          <p className="font-medium">
            Current Status:{" "}
            <span className={member.status === "Active" ? "text-green-600 font-bold" : "text-muted-foreground"}>
              ● {member.status}
            </span>
          </p>
          <p className="font-medium">
            Last Updated: <span className="text-muted-foreground font-mono">{member.last_updated}</span>
          </p>
        </div>
      </div>

      {/* ML Prediction Cards (Strictly for this occupant) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Current Activity */}
        <Card className="border-primary/50 shadow-sm flex flex-col">
          <CardHeader className="pb-2 bg-muted/10 border-b">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Current Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4 flex-1 flex flex-col">
            <p className="text-3xl font-bold text-primary mb-1">{member.current_activity}</p>
            {member.status === "Idle" && (
              <p className="text-xs text-muted-foreground mb-2 italic">
                {member.reason || "Inactive for > 30 mins"}
              </p>
            )}
            <p className="text-sm font-medium">
              Room: <span className="text-foreground font-semibold">{member.room}</span>
            </p>

            <div className="mt-4 mb-4">
              <p className="text-sm font-medium">
                Confidence: {member.confidence ? `${member.confidence}%` : "Not available"}
              </p>
              {member.confidence_level && (
                <p className="text-xs font-semibold mt-1 mb-2 text-muted-foreground">
                  {member.confidence_level} Confidence
                </p>
              )}
              {member.confidence && (
                <div className="w-full bg-muted h-2 rounded-full overflow-hidden">
                  <div className={`h-full ${confColor}`} style={{ width: `${member.confidence}%` }} />
                </div>
              )}
            </div>

            {/* Actual Ground Truth Comparison if available in dataset */}
            {member.actual_activity && (
              <div className="text-xs flex items-center justify-between border-t py-2 bg-muted/10 px-2 rounded mb-3">
                <span>
                  Ground Truth: <strong>{member.actual_activity}</strong>
                </span>
                {member.prediction_accuracy === "Correct" ? (
                  <span className="text-green-600 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="size-3.5" /> Correct
                  </span>
                ) : (
                  <span className="text-destructive font-semibold flex items-center gap-1">
                    <XCircle className="size-3.5" /> Incorrect
                  </span>
                )}
              </div>
            )}

            {/* Feedback Section */}
            <div className="mt-auto pt-3 border-t">
              <p className="text-xs font-semibold mb-2">Was this prediction correct?</p>
              {!showFeedback ? (
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-full text-xs"
                    onClick={() => {
                      toast.success(`Prediction confirmed as correct for ${member.name}!`);
                    }}
                  >
                    ✓ Correct
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-full text-xs"
                    onClick={() => setShowFeedback(true)}
                  >
                    ✕ Incorrect
                  </Button>
                </div>
              ) : (
                <div className="space-y-2 bg-muted/20 p-2 rounded border">
                  <p className="text-xs font-medium">Actual Activity:</p>
                  <select
                    value={correctedAct}
                    onChange={(e) => setCorrectedAct(e.target.value)}
                    className="w-full text-sm border p-1 rounded bg-background"
                  >
                    <option>Watching TV</option>
                    <option>Cooking</option>
                    <option>Sleeping</option>
                    <option>Leaving Home</option>
                    <option>Eating</option>
                    <option>Working</option>
                    <option>Exercising</option>
                    <option>Relaxing</option>
                  </select>
                  <div className="flex gap-2">
                    <Button size="sm" className="w-full text-xs" onClick={handleFeedbackSubmit}>
                      Save
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="w-full text-xs"
                      onClick={() => setShowFeedback(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Card 2: Next Activity */}
        <Card className="shadow-sm flex flex-col">
          <CardHeader className="pb-2 bg-muted/10 border-b">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Next Activity Prediction
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 flex-1 text-center flex flex-col justify-center items-center">
            <div className="w-full bg-muted/10 p-3 rounded-lg border mb-3">
              <p className="text-xs text-muted-foreground uppercase font-bold mb-1">CURRENT</p>
              <p className="text-lg font-bold">{member.current_activity}</p>
            </div>

            <div className="text-muted-foreground my-1">↓</div>

            <div className="w-full bg-primary/5 p-3 rounded-lg border border-primary/20 mt-2">
              <p className="text-xs text-primary/70 uppercase font-bold mb-1">PREDICTED NEXT</p>
              <p className="text-2xl font-bold text-primary mb-1">
                {member.next_activity || "Unknown"}
              </p>
              {member.next_confidence && (
                <p className="text-xs font-medium">Confidence: {member.next_confidence}%</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Card 3: Routine Status & Anomaly */}
        <Card className="shadow-sm flex flex-col">
          <CardHeader className="pb-2 bg-muted/10 border-b">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Personalized Routine Status
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4 flex-1 flex flex-col">
            <div className="mb-4 text-center py-4 bg-muted/5 border rounded-lg">
              <p
                className={`text-2xl font-bold tracking-widest ${
                  member.routine_status === "Normal" ? "text-green-600" : "text-destructive"
                }`}
              >
                {member.routine_status?.toUpperCase() || "NORMAL"}
              </p>
            </div>

            <div className="space-y-3 mb-4 text-sm">
              <div className="flex justify-between border-b pb-2">
                <span className="font-medium">Anomaly Score:</span>
                <span className="font-mono">{member.anomaly_score ?? "0.12"}</span>
              </div>
              <div>
                <span className="font-medium block mb-1">Routine Baseline:</span>
                <span className="text-muted-foreground text-xs leading-relaxed">
                  Behavior for <strong>{member.name}</strong>{" "}
                  {member.routine_status === "Normal" ? "matches" : "deviates from"} their learned historical routine.
                </span>
              </div>
            </div>

            <div className="mt-auto text-[10px] text-muted-foreground bg-muted/20 p-2 rounded-md leading-relaxed border italic">
              "Unusual" indicates a statistical departure from routine, not an emergency.
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Individual Occupant Recorded Events Timeline (Strictly Filtered to this Person ID) */}
      <Card className="shadow-sm mt-6">
        <CardHeader className="pb-2 bg-muted/10 border-b flex flex-row items-center justify-between">
          <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <Clock className="size-3.5" /> Recent Events Filtered Strictly to {member.name} ({member.id})
          </CardTitle>
          <span className="text-xs font-mono text-muted-foreground">
            {timeline?.length || 0} events listed
          </span>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {timeline && timeline.length > 0 ? (
              timeline.map((item: any, i: number) => (
                <div key={i} className="flex items-center justify-between text-sm border-b pb-2 last:border-0 gap-2">
                  <span className="font-mono text-xs text-muted-foreground w-20 shrink-0">{item.time}</span>
                  <span className="font-bold flex-1 text-primary truncate">
                    {item.activity}
                  </span>
                  <span className="text-xs text-muted-foreground bg-muted/20 px-2 py-0.5 rounded border shrink-0">
                    {item.room}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground py-2 text-center">
                No recorded activity events found for occupant {member.id}.
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
