import { Link, useRouterState } from "@tanstack/react-router";
import {
  Activity, BarChart3, Database, FileUp, ShieldAlert,
  Zap, Bot, LayoutDashboard, Settings as SettingsIcon, LineChart, FileSignature, Clock, TrendingUp, ShieldCheck, Cpu
} from "lucide-react";
import {
  Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent,
  SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarFooter
} from "@/components/ui/sidebar";

const items = [
  { title: "Overview", url: "/", icon: LayoutDashboard },
  { title: "Activity Intelligence", url: "/activity", icon: Activity },
  { title: "My Routine", url: "/routine", icon: BarChart3 },
  { title: "Timeline", url: "/timeline", icon: Clock },
  { title: "Predictions", url: "/predictions", icon: TrendingUp },
  { title: "Routine Changes", url: "/changes", icon: ShieldAlert },
  { title: "Data Center", url: "/ingestion", icon: FileUp },
  { title: "Dataset Explorer", url: "/explorer", icon: Database },
  { title: "Energy Insights", url: "/energy", icon: Zap },
  { title: "Appliance Insights", url: "/appliances", icon: Cpu },
  { title: "ML Evaluation", url: "/evaluation", icon: FileSignature },
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
            <p className="truncate text-sm font-semibold">PersonaSense AI</p>
            <p className="truncate text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Privacy-Preserving</p>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-xs font-semibold text-slate-400 tracking-wider">CORE INTELLIGENCE</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.slice(0, 6).map((item) => (
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
        
        <SidebarGroup>
          <SidebarGroupLabel className="text-xs font-semibold text-slate-400 tracking-wider">DATA & ANALYSIS</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.slice(6).map((item) => (
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
      <SidebarFooter className="p-4 border-t bg-slate-50">
          <div className="flex flex-col gap-2 group-data-[collapsible=icon]:hidden">
              <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500">Dataset Status</span>
                  <span className="text-xs font-bold text-green-600 flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>ML Ready</span>
              </div>
              <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500">Privacy</span>
                  <span className="text-xs font-bold text-blue-600 flex items-center gap-1"><ShieldCheck className="size-3"/>Protected</span>
              </div>
          </div>
          <div className="hidden group-data-[collapsible=icon]:flex flex-col items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              <ShieldCheck className="size-4 text-blue-600"/>
          </div>
      </SidebarFooter>
    </Sidebar>
  );
}
