"use client"

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

export default function Dashboard() {
  return (
    <>
      <header className="flex h-16 shrink-0 items-center justify-between border-b px-4 md:px-6 bg-white text-black">
        <div className="flex items-center gap-2">
          <SidebarTrigger className="mr-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem className="hidden md:block">
                <BreadcrumbLink href="#" className="text-mercurios-lightBlue">
                  Earth
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator className="hidden md:block" />
              <BreadcrumbItem>
                <BreadcrumbPage>Overview</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </div>
        <NavUser
          user={{
            name: "Julius",
            email: "julius@mercurios.ai",
            avatar:
              "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Screenshot%202025-02-12%20at%2014.37.00-eWxWp4zDU9wfmJUclaheErKjfbxFXO.png",
          }}
        />
      </header>
      <main className="flex-1 overflow-auto bg-gray-50">
        <div className="container mx-auto py-6 px-4 md:px-6">
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
            </TabsList>
            <TabsContent value="overview" className="space-y-4">
              <UserStats />
              <div className="grid gap-6 lg:grid-cols-2">
                <PieChart />
                <BarChart />
              </div>
              <div className="w-full">
                <AreaChart />
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </>
  )
}

