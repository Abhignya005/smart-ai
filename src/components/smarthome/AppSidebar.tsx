import { Link, useRouterState } from "@tanstack/react-router";
import {
  Activity, BarChart3, Database, FileUp, ShieldAlert,
  Zap, Bot, LayoutDashboard, Settings as SettingsIcon, LineChart, FileSignature
} from "lucide-react";
import {
  Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent,
  SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem,
} from "@/components/ui/sidebar";

const items = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Data Ingestion", url: "/ingestion", icon: FileUp },
  { title: "Dataset Explorer", url: "/explorer", icon: Database },
  { title: "Activity Recognition", url: "/activity", icon: Activity },
  { title: "Routine Discovery", url: "/routine", icon: BarChart3 },
  { title: "ML Evaluation", url: "/evaluation", icon: FileSignature },
  { title: "AI Assistant", url: "/assistant", icon: Bot },
  { title: "Anomaly Detection", url: "/anomalies", icon: ShieldAlert },
  { title: "Energy Intelligence", url: "/energy", icon: Zap },
  { title: "Settings & Privacy", url: "/settings", icon: SettingsIcon },
] as const;

export function AppSidebar() {
  const pathname = useRouterState({ select: (r) => r.location.pathname });

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-3 py-4">
        <div className="flex items-center gap-2">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Activity className="size-4" />
          </div>
          <div className="min-w-0 group-data-[collapsible=icon]:hidden">
            <p className="truncate text-sm font-semibold">SmartHome AI</p>
            <p className="truncate text-xs text-muted-foreground">Privacy-Preserving ML</p>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Analytics Platform</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.url}>
                  <SidebarMenuButton asChild isActive={pathname === item.url} tooltip={item.title}>
                    <Link to={item.url}>
                      <item.icon className="size-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
