"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { UserStats } from "./components/user-stats"
import { AppPerformance } from "./components/app-performance"
import { Insights } from "./components/insights"
import { UserFeedback } from "./components/user-feedback"
import { DashboardSidebar } from "./components/dashboard-sidebar"
import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"

export default function Dashboard() {
  return (
    <SidebarProvider>
      <div className="flex h-screen">
        <DashboardSidebar />
        <SidebarInset className="flex-1 overflow-auto">
          <div className="container mx-auto p-6">
            <header className="mb-6 flex items-center">
              <SidebarTrigger className="mr-4 lg:hidden" />
              <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
            </header>
            <Tabs defaultValue="user-stats" className="space-y-4">
              <TabsList>
                <TabsTrigger value="user-stats">User Stats</TabsTrigger>
                <TabsTrigger value="app-performance">App Performance</TabsTrigger>
                <TabsTrigger value="insights">Insights</TabsTrigger>
                <TabsTrigger value="user-feedback">User Feedback</TabsTrigger>
              </TabsList>
              <TabsContent value="user-stats">
                <UserStats />
              </TabsContent>
              <TabsContent value="app-performance">
                <AppPerformance />
              </TabsContent>
              <TabsContent value="insights">
                <Insights />
              </TabsContent>
              <TabsContent value="user-feedback">
                <UserFeedback />
              </TabsContent>
            </Tabs>
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  )
}

