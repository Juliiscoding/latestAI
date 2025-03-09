"use client"

import React from "react"
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Link from "next/link"
import { BarChart, ArrowUpRight, Upload, Image, Users, Settings, Bell } from "lucide-react"

export default function ManufacturerPage() {
  // Mock data for the dashboard
  const stats = [
    { title: "Total Products", value: "247", change: "+12% from last month", icon: <BarChart className="h-4 w-4 text-muted-foreground" /> },
    { title: "Retailer Views", value: "1,234", change: "+18% from last month", icon: <ArrowUpRight className="h-4 w-4 text-muted-foreground" /> },
    { title: "Data Completeness", value: "92%", change: "+5% from last month", icon: <Upload className="h-4 w-4 text-muted-foreground" /> },
    { title: "Active Retailers", value: "28", change: "+3 from last month", icon: <Users className="h-4 w-4 text-muted-foreground" /> },
  ];

  const recentUploads = [
    { id: 1, name: "Summer Collection 2025", type: "Product Data", date: "2025-03-08", status: "Processed" },
    { id: 2, name: "Inventory Update March", type: "Inventory", date: "2025-03-07", status: "Processed" },
    { id: 3, name: "New Product Images", type: "Media", date: "2025-03-05", status: "Processed" },
    { id: 4, name: "Price Updates Q2", type: "Product Data", date: "2025-03-02", status: "Processed" },
  ];

  const notifications = [
    { id: 1, message: "Your product data has been successfully processed", date: "2025-03-08", read: false },
    { id: 2, message: "5 retailers viewed your new summer collection", date: "2025-03-07", read: false },
    { id: 3, message: "Inventory update completed successfully", date: "2025-03-07", read: true },
    { id: 4, message: "Media assets processed and available to retailers", date: "2025-03-05", read: true },
  ];

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <SidebarInset className="flex-1 overflow-auto w-full">
        <div className="w-full h-full p-4 sm:p-6 overflow-x-hidden">
          <header className="mb-6 flex items-center justify-between">
            <div className="flex items-center">
              <SidebarTrigger className="mr-4" />
              <h1 className="text-3xl font-bold">Brand Dashboard</h1>
            </div>
            <div className="flex gap-2">
              <Button asChild>
                <Link href="/hyperion/manufacturer/upload-product-data">Upload Product Data</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/hyperion/manufacturer/upload-marketing-media">Upload Marketing Media</Link>
              </Button>
            </div>
          </header>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
            {stats.map((stat, index) => (
              <Card key={index}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                  {stat.icon}
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-muted-foreground">{stat.change}</p>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <div className="grid gap-6 md:grid-cols-3 mb-8">
            <Card className="col-span-1">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common tasks and actions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start" asChild>
                  <Link href="/hyperion/manufacturer/upload-product-data" className="flex items-center">
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Product Data
                  </Link>
                </Button>
                <Button variant="outline" className="w-full justify-start" asChild>
                  <Link href="/hyperion/manufacturer/upload-marketing-media" className="flex items-center">
                    <Image className="mr-2 h-4 w-4" />
                    Upload Marketing Media
                  </Link>
                </Button>
                <Button variant="outline" className="w-full justify-start" asChild>
                  <Link href="/hyperion/manufacturer/retailers" className="flex items-center">
                    <Users className="mr-2 h-4 w-4" />
                    Manage Retailers
                  </Link>
                </Button>
                <Button variant="outline" className="w-full justify-start" asChild>
                  <Link href="/hyperion/manufacturer/settings" className="flex items-center">
                    <Settings className="mr-2 h-4 w-4" />
                    Account Settings
                  </Link>
                </Button>
              </CardContent>
            </Card>
            
            <Card className="col-span-2">
              <CardHeader>
                <CardTitle>Recent Uploads</CardTitle>
                <CardDescription>Your latest data uploads and their status</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentUploads.map((upload) => (
                    <div key={upload.id} className="flex items-center justify-between border-b pb-2 last:border-0 last:pb-0">
                      <div>
                        <p className="font-medium">{upload.name}</p>
                        <div className="flex items-center text-sm text-muted-foreground">
                          <span>{upload.type}</span>
                          <span className="mx-2">•</span>
                          <span>{upload.date}</span>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          upload.status === "Processed" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                        }`}>
                          {upload.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
          
          <div className="grid gap-6 md:grid-cols-3 mb-8">
            <Card className="col-span-1">
              <CardHeader className="flex flex-row items-center justify-between space-y-0">
                <div>
                  <CardTitle>Notifications</CardTitle>
                  <CardDescription>Recent system notifications</CardDescription>
                </div>
                <Bell className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {notifications.map((notification) => (
                    <div key={notification.id} className="flex items-start gap-4 border-b pb-4 last:border-0 last:pb-0">
                      <div className={`mt-0.5 h-2 w-2 rounded-full ${notification.read ? 'bg-muted' : 'bg-primary'}`} />
                      <div>
                        <p className={`text-sm ${notification.read ? 'text-muted-foreground' : 'font-medium'}`}>
                          {notification.message}
                        </p>
                        <p className="text-xs text-muted-foreground">{notification.date}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            <Card className="col-span-2">
              <CardHeader>
                <CardTitle>Retailer Activity</CardTitle>
                <CardDescription>Recent retailer interactions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[200px]">
                  <div className="flex h-full items-center justify-center">
                    <p className="text-muted-foreground">Retailer activity chart will be displayed here</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarInset>
    </div>
  )
}
