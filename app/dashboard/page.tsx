"use client"

import { useState, useEffect } from "react"
import { UserStats } from "@/components/user-stats"
import { SidebarTrigger } from "@/components/ui/sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { PieChart } from "@/components/charts/pie-chart"
import { AreaChart } from "@/components/charts/area-chart"
import { BarChart } from "@/components/charts/bar-chart"
import { NavUser } from "@/components/nav-user"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useTenantContext, TenantProvider } from "./components/tenant-context"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"

// Wrapper-Komponente für das Dashboard mit Tenant-Kontext
export default function DashboardWithTenant() {
  return (
    <TenantProvider>
      <Dashboard />
    </TenantProvider>
  );
}

// Eigentliche Dashboard-Komponente, die den Tenant-Kontext verwendet
function Dashboard() {
  const { tenant, isLoading, error } = useTenantContext();
  const [userData, setUserData] = useState<any>(null);
  const [isUserDataLoading, setIsUserDataLoading] = useState(true);

  // Benutzerdaten laden basierend auf dem aktuellen Tenant
  useEffect(() => {
    async function loadUserData() {
      if (!tenant) return;
      
      try {
        setIsUserDataLoading(true);
        const response = await fetch(`/api/dashboard/user?tenantId=${tenant.id}`);
        if (response.ok) {
          const data = await response.json();
          setUserData(data);
        }
      } catch (error) {
        console.error("Error loading user data:", error);
      } finally {
        setIsUserDataLoading(false);
      }
    }

    if (tenant) {
      loadUserData();
    }
  }, [tenant]);

  // Zeige Ladeanzeige während der Tenant geladen wird
  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-[#6ACBDF]"></div>
      </div>
    );
  }

  // Fehlerbehandlung
  if (error || !tenant) {
    return (
      <div className="flex h-screen w-full items-center justify-center p-4">
        <Alert className="max-w-md">
          <AlertTitle>Fehler beim Laden des Dashboards</AlertTitle>
          <AlertDescription>
            {error || "Es wurde kein Tenant gefunden. Bitte kontaktieren Sie den Administrator."}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <>
      <header className="flex h-16 shrink-0 items-center justify-between border-b px-4 md:px-6 bg-white text-black">
        <div className="flex items-center gap-2">
          <SidebarTrigger className="mr-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem className="hidden md:block">
                <BreadcrumbLink href="#" className="text-mercurios-lightBlue">
                  {tenant.name}
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator className="hidden md:block" />
              <BreadcrumbItem>
                <BreadcrumbPage>Dashboard</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </div>
        <NavUser
          user={userData?.user || {
            name: "Benutzer",
            email: "benutzer@mercurios.ai",
            avatar: "",
          }}
        />
      </header>
      <main className="flex-1 overflow-auto bg-gray-50">
        <div className="container mx-auto py-6 px-4 md:px-6">
          <h1 className="mb-4 text-2xl font-bold">{tenant.name} Dashboard</h1>
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList>
              <TabsTrigger value="overview">Übersicht</TabsTrigger>
              <TabsTrigger value="analytics">Analysen</TabsTrigger>
              <TabsTrigger value="insights">KI-Insights</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-4">
              {isUserDataLoading ? (
                <div className="grid gap-6">
                  <Skeleton className="h-48" />
                  <div className="grid gap-6 lg:grid-cols-2">
                    <Skeleton className="h-72" />
                    <Skeleton className="h-72" />
                  </div>
                </div>
              ) : (
                <>
                  <UserStats tenantId={tenant.id} />
                  <div className="grid gap-6 lg:grid-cols-2">
                    <PieChart />
                    <BarChart />
                  </div>
                  <div className="w-full">
                    <AreaChart />
                  </div>
                </>
              )}
            </TabsContent>
            
            <TabsContent value="analytics" className="space-y-4">
              <div className="rounded-lg border bg-card p-6 shadow-sm">
                <h3 className="text-xl font-semibold mb-4">Tenant-spezifische Analysen</h3>
                <p className="text-gray-500">Hier werden tiefergehende Analysen für {tenant.name} angezeigt.</p>
              </div>
            </TabsContent>
            
            <TabsContent value="insights" className="space-y-4">
              <div className="rounded-lg border bg-card p-6 shadow-sm">
                <h3 className="text-xl font-semibold mb-4">KI-generierte Insights</h3>
                <p className="text-gray-500">KI-basierte Erkenntnisse aus Ihren Daten werden hier angezeigt.</p>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </>
  )
}

