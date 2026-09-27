import { Link, useRouterState } from "@tanstack/react-router";
import {
  Activity,
  AlarmClock,
  BarChart3,
  Cpu,
  Home,
  Settings as SettingsIcon,
  ShieldAlert,
  Zap,
  Bot
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const items = [
  { title: "ML Overview Dashboard", url: "/", icon: Home },
  { title: "Energy Forecasting", url: "/appliance", icon: Zap },
  { title: "Dataset Analysis", url: "/sensors", icon: Cpu },
  { title: "Activity Recognition", url: "/activity", icon: Activity },
  { title: "Behavioral Pattern Learning", url: "/routine", icon: BarChart3 },
  { title: "ML Anomaly Detection", url: "/anomalies", icon: ShieldAlert },
  { title: "Model Insights", url: "/models", icon: Bot },
] as const;

export function AppSidebar() {
  const pathname = useRouterState({ select: (r) => r.location.pathname });

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-3 py-4">
        <div className="flex items-center gap-2">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Home className="size-4" />
          </div>
          <div className="min-w-0 group-data-[collapsible=icon]:hidden">
            <p className="truncate text-sm font-semibold">SmartHome AI</p>
            <p className="truncate text-xs text-muted-foreground">Routine Intelligence</p>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Workspace</SidebarGroupLabel>
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
