"use client"

import { Suspense } from "react"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, Filter } from "lucide-react"
import { Separator } from "@/components/ui/separator"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { SidebarTrigger } from "@/components/ui/sidebar"

const tabs = [
  { id: "inbox", label: "Inbox" },
  { id: "campaigns", label: "Campaigns" },
  { id: "audience", label: "Audience" },
  { id: "reviews", label: "Reviews" },
  { id: "automations", label: "Automations" },
  { id: "insights", label: "Insights" },
]

function WhatsAppContent() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const currentTab = searchParams.get("tab") || "inbox"

  const handleTabChange = (tabId: string) => {
    router.push(`${pathname}?tab=${tabId}`, { scroll: false })
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`
                whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium
                ${
                  currentTab === tab.id
                    ? "border-primary text-primary"
                    : "border-transparent text-muted-foreground hover:border-gray-300 hover:text-foreground"
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {currentTab === "inbox" && (
        <Card>
          <CardHeader>
            <CardTitle>Campaign Overview</CardTitle>
            <CardDescription>
              Manage your marketing & ad-hoc campaigns, plan your campaigns in advance and keep your customers informed
              at all times.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium">Campaign Analytics for</span>
                <select className="text-sm border rounded-md p-1">
                  <option>Last 30 Days</option>
                  <option>Last 7 Days</option>
                  <option>All Time</option>
                </select>
                <select className="text-sm border rounded-md p-1">
                  <option>All Channels</option>
                  <option>WhatsApp</option>
                  <option>SMS</option>
                </select>
              </div>
              <Button variant="default">Create Campaign</Button>
            </div>

            <div className="text-center py-8 text-sm text-muted-foreground">
              No campaign messages have been sent during this period. Plan the first campaign now.
            </div>

            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <p className="text-sm font-medium">
                  Campaigns Sent: <span className="font-bold">0</span>
                </p>
                <p className="text-sm font-medium">
                  Messages Sent: <span className="font-bold">0</span>
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">
                  Reached Contacts: <span className="font-bold">0</span>
                </p>
                <p className="text-sm font-medium">
                  Sending Errors: <span className="font-bold">0</span>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {currentTab === "audience" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Contacts</CardTitle>
                <CardDescription>Find all contact information here</CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline">
                  <Filter className="mr-2 h-4 w-4" />
                  Filter
                </Button>
                <Button>+ Create</Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2 mb-4">
              <Search className="h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search" className="max-w-sm" />
            </div>

            <div className="rounded-md border">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="h-10 px-4 text-left align-middle font-medium">Name</th>
                    <th className="h-10 px-4 text-left align-middle font-medium">Phone</th>
                    <th className="h-10 px-4 text-left align-middle font-medium">Date</th>
                    <th className="h-10 px-4 text-right align-middle font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b">
                    <td className="p-4">Schmidt</td>
                    <td className="p-4">+491731441459</td>
                    <td className="p-4">1 week ago</td>
                    <td className="p-4 text-right">•••</td>
                  </tr>
                  <tr className="border-b">
                    <td className="p-4">Advertising Business Support</td>
                    <td className="p-4">+9799162625</td>
                    <td className="p-4">4 days ago</td>
                    <td className="p-4 text-right">•••</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {currentTab === "campaigns" && (
        <Card>
          <CardHeader>
            <CardTitle>Campaigns</CardTitle>
            <CardDescription>Manage your WhatsApp campaigns</CardDescription>
          </CardHeader>
          <CardContent>
            {/* Add campaigns content here */}
            <div className="text-center py-8 text-sm text-muted-foreground">
              No campaigns created yet. Create your first campaign.
            </div>
          </CardContent>
        </Card>
      )}

      {currentTab === "reviews" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Reviews & Ratings</CardTitle>
                <CardDescription>Monitor and manage customer feedback and ratings</CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline">
                  <Filter className="mr-2 h-4 w-4" />
                  Filter
                </Button>
                <Button>Export</Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2 mb-4">
              <Search className="h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search reviews" className="max-w-sm" />
            </div>

            <div className="rounded-md border">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="h-10 px-4 text-left align-middle font-medium">Customer</th>
                    <th className="h-10 px-4 text-left align-middle font-medium">Rating</th>
                    <th className="h-10 px-4 text-left align-middle font-medium">Comment</th>
                    <th className="h-10 px-4 text-left align-middle font-medium">Date</th>
                    <th className="h-10 px-4 text-right align-middle font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b">
                    <td className="p-4">John Doe</td>
                    <td className="p-4">★★★★★</td>
                    <td className="p-4">Great customer service and quick response!</td>
                    <td className="p-4">2 days ago</td>
                    <td className="p-4 text-right">•••</td>
                  </tr>
                  <tr className="border-b">
                    <td className="p-4">Jane Smith</td>
                    <td className="p-4">★★★★☆</td>
                    <td className="p-4">Very helpful team, minor delay in delivery</td>
                    <td className="p-4">1 week ago</td>
                    <td className="p-4 text-right">•••</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {currentTab === "automations" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Automated Responses</CardTitle>
                <CardDescription>Set up and manage automated message responses</CardDescription>
              </div>
              <Button>Create Automation</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">Welcome Message</CardTitle>
                    <div className="flex items-center space-x-2">
                      <div className="flex h-6 items-center rounded-full bg-green-100 px-2 text-xs font-semibold text-green-700">
                        Active
                      </div>
                      <Button variant="ghost" size="sm">
                        Edit
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Sends an automated welcome message to new contacts</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">Out of Office</CardTitle>
                    <div className="flex items-center space-x-2">
                      <div className="flex h-6 items-center rounded-full bg-gray-100 px-2 text-xs font-semibold text-gray-700">
                        Inactive
                      </div>
                      <Button variant="ghost" size="sm">
                        Edit
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Responds to messages received outside business hours</p>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>
      )}

      {currentTab === "insights" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Analytics & Insights</CardTitle>
                <CardDescription>Track and analyze your WhatsApp business performance</CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <select className="text-sm border rounded-md p-1">
                  <option>Last 30 Days</option>
                  <option>Last 7 Days</option>
                  <option>All Time</option>
                </select>
                <Button variant="outline">Export Report</Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Messages</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">2,345</div>
                  <p className="text-xs text-muted-foreground">+20% from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Response Rate</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">92%</div>
                  <p className="text-xs text-muted-foreground">+5% from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">5m</div>
                  <p className="text-xs text-muted-foreground">-2m from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Customer Satisfaction</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">4.8/5</div>
                  <p className="text-xs text-muted-foreground">+0.3 from last month</p>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default function WhatsAppPanel() {
  return (
    <>
      <header className="flex h-16 shrink-0 items-center gap-2 border-b">
        <div className="flex items-center gap-2 px-3">
          <SidebarTrigger />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem className="hidden md:block">
                <BreadcrumbLink href="#">Moon</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator className="hidden md:block" />
              <BreadcrumbItem>
                <BreadcrumbPage>WhatsApp</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </div>
      </header>
      <Suspense fallback={<div>Loading...</div>}>
        <WhatsAppContent />
      </Suspense>
    </>
  )
}

