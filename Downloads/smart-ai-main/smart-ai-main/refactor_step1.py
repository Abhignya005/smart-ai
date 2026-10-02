import os
import shutil

BASE_DIR = r"c:\Users\abhignya\Downloads\my-smart-beat-main\my-smart-beat-main"
ROUTES_DIR = os.path.join(BASE_DIR, "src", "routes")
COMPONENTS_DIR = os.path.join(BASE_DIR, "src", "components", "smarthome")

# 1. Update AppSidebar.tsx
sidebar_code = """import { Link, useRouterState } from "@tanstack/react-router";
import {
  Activity, BarChart3, Database, FileUp, ShieldAlert,
  Zap, Bot, LayoutDashboard, Settings as SettingsIcon, LineChart, Server, Cpu
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
  { title: "Anomaly Detection", url: "/anomalies", icon: ShieldAlert },
  { title: "Energy Intelligence", url: "/energy", icon: Zap },
  { title: "Energy Forecasting", url: "/forecast", icon: LineChart },
  { title: "Appliance Intelligence", url: "/appliances", icon: Cpu },
  { title: "Model Center", url: "/models", icon: Server },
  { title: "AI Assistant", url: "/assistant", icon: Bot },
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
"""

with open(os.path.join(COMPONENTS_DIR, "AppSidebar.tsx"), "w") as f:
    f.write(sidebar_code)

# 2. Cleanup old unused routes to prevent duplicates/errors
old_routes = ["appliance.tsx", "sensors.tsx", "plan.tsx"]
for r in old_routes:
    p = os.path.join(ROUTES_DIR, r)
    if os.path.exists(p):
        os.remove(p)

print("Removed old routes and updated sidebar.")

