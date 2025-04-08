"use client"

import * as React from "react"
import { useRouter, usePathname } from "next/navigation"
import { Home, Search, MessageSquare, Bot, BarChart, Brain, MessageCircle, Cog, ChevronDown, ChevronRight } from "lucide-react"
import { Input } from "@/components/ui/input"
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarMenuSubButton,
  useSidebar,
} from "@/components/ui/sidebar"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

interface NavSection {
  id: string
  icon: React.ComponentType<{ className?: string }>
  emoji?: string
  label: string
  href?: string
  items?: {
    label: string
    href: string
  }[]
}

const navSections: NavSection[] = [
  {
    id: "home",
    icon: Home,
    label: "Home",
    href: "/",
  },
  {
    id: "inbox",
    icon: MessageSquare,
    label: "Inbox",
    href: "/inbox",
  },
  {
    id: "ask-ai",
    icon: Bot,
    label: "Ask AI",
    href: "/ask-ai",
  },
  {
    id: "earth",
    icon: BarChart,
    emoji: "🌍",
    label: "EARTH",
    items: [
      { label: "Dashboard", href: "/dashboard" },
      { label: "Business Intelligence", href: "/dashboard/business-intelligence" },
      { label: "Sales Analytics", href: "/earth/sales" },
      { label: "Product & Inventory Analysis", href: "/earth/inventory" },
      { label: "Customer Analysis & Segmentation", href: "/earth/customers" },
    ],
  },
  {
    id: "hyperion",
    icon: BarChart,
    emoji: "🔆",
    label: "HYPERION",
    items: [
      { label: "Home", href: "/hyperion" },
      { label: "Product Data", href: "/hyperion/product-data" },
      { label: "Marketing Media", href: "/hyperion/marketing-media" },
      { label: "Brands", href: "/hyperion/brands" },
      { label: "Order History", href: "/hyperion/order-history" },
      { label: "Insights", href: "/hyperion/insights" },
      { label: "Manufacturer Portal", href: "/hyperion/manufacturer" },
    ],
  },
  {
    id: "saturn",
    icon: Brain,
    emoji: "🪐",
    label: "SATURN",
    items: [
      { label: "Predictive Analytics", href: "/saturn/predictive" },
      { label: "Scenario Simulation", href: "/saturn/simulation" },
      { label: "External Data Integration", href: "/saturn/integration" },
    ],
  },
  {
    id: "neptun",
    icon: MessageCircle,
    emoji: "🌊",
    label: "NEPTUN",
    items: [
      { label: "Customer Support & Chatbot", href: "/neptun/support" },
      { label: "Marketing & Personalization", href: "/neptun/marketing" },
      { label: "Omnichannel Management", href: "/neptun/omnichannel" },
    ],
  },
  {
    id: "moon",
    icon: MessageCircle,
    emoji: "🌙",
    label: "MOON",
    items: [
      { label: "WhatsApp", href: "/whatsapp" },
      { label: "Instagram", href: "/moon/instagram" },
      { label: "X (Twitter)", href: "/moon/twitter" },
      { label: "Community Engagement", href: "/moon/community" },
    ],
  },
  {
    id: "settings",
    icon: Cog,
    emoji: "⚙️",
    label: "EINSTELLUNGEN",
    items: [
      { label: "User Management", href: "/settings/users" },
      { label: "API Management", href: "/settings/api" },
      { label: "System & Notifications", href: "/settings/system" },
    ],
  },
]

export function NavMain({ collapsed }: { collapsed: boolean }) {
  const [searchQuery, setSearchQuery] = React.useState("")
  const [openSections, setOpenSections] = React.useState<string[]>([])
  const router = useRouter()
  const pathname = usePathname()
  const { toggleSidebar } = useSidebar()

  const toggleSection = (sectionId: string) => {
    setOpenSections((prev) => (prev.includes(sectionId) ? prev.filter((id) => id !== sectionId) : [...prev, sectionId]))
  }

  const isActive = (href: string) => pathname === href

  return (
    <SidebarGroup>
      <SidebarGroupContent>
        {!collapsed && (
          <div className="px-2 py-2">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        )}
        <SidebarMenu className="space-y-1 px-2">
          {navSections.map((section) => (
            <SidebarMenuItem key={section.id}>
              {section.items ? (
                <>
                  {collapsed ? (
                    <Tooltip delayDuration={0}>
                      <TooltipTrigger asChild>
                        <SidebarMenuButton
                          onClick={() => toggleSection(section.id)}
                          className={cn(
                            "w-full justify-center mb-1 hover:bg-accent rounded-md transition-all duration-200 ease-in-out",
                            "px-2 py-2",
                          )}
                        >
                          <div className="flex items-center justify-center relative">
                            {section.emoji ? (
                              <span className="text-lg">{section.emoji}</span>
                            ) : (
                              <span className="flex items-center justify-center">
                                {React.createElement(section.icon, { className: "h-5 w-5" })}
                              </span>
                            )}
                            {openSections.includes(section.id) && (
                              <div className="absolute right-[-4px] bottom-[-4px] h-2 w-2 rounded-full bg-primary"></div>
                            )}
                          </div>
                        </SidebarMenuButton>
                      </TooltipTrigger>
                      <TooltipContent side="right" className="font-medium">
                        {section.label}
                      </TooltipContent>
                    </Tooltip>
                  ) : (
                    <SidebarMenuButton
                      onClick={() => toggleSection(section.id)}
                      className={cn(
                        "w-full justify-between mb-1 hover:bg-accent rounded-md transition-all duration-200 ease-in-out",
                        "px-3 py-2",
                      )}
                    >
                      <div className="flex items-center">
                        {section.emoji ? (
                          <span className="text-lg mr-2">{section.emoji}</span>
                        ) : (
                          <span className="mr-2">
                            {React.createElement(section.icon, { className: "h-5 w-5" })}
                          </span>
                        )}
                        <span className="truncate">{section.label}</span>
                      </div>
                      <ChevronDown
                        className={cn(
                          "h-4 w-4 transition-transform duration-200",
                          openSections.includes(section.id) && "rotate-180",
                        )}
                      />
                    </SidebarMenuButton>
                  )}
                  {!collapsed && openSections.includes(section.id) && (
                    <SidebarMenuSub className="space-y-1 py-2 pl-4">
                      {section.items.map((item) => (
                        <SidebarMenuSubItem key={item.href}>
                          <SidebarMenuSubButton
                            className={cn(
                              "px-3 py-1.5 w-full text-sm hover:bg-accent rounded-md transition-colors duration-200",
                              "whitespace-normal text-left",
                              isActive(item.href) && "bg-accent text-accent-foreground font-medium",
                            )}
                            onClick={() => router.push(item.href)}
                          >
                            <span className="block truncate">{item.label}</span>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      ))}
                    </SidebarMenuSub>
                  )}
                  {collapsed && openSections.includes(section.id) && (
                    <div className="py-1 px-1">
                      {section.items.map((item) => (
                        <Tooltip key={item.href} delayDuration={0}>
                          <TooltipTrigger asChild>
                            <button
                              className={cn(
                                "w-full flex items-center justify-center p-1.5 rounded-md text-xs hover:bg-accent transition-colors duration-200",
                                isActive(item.href) && "bg-accent text-accent-foreground font-medium",
                              )}
                              onClick={() => router.push(item.href)}
                            >
                              <ChevronRight className="h-3 w-3" />
                            </button>
                          </TooltipTrigger>
                          <TooltipContent side="right" className="font-medium text-sm">
                            {item.label}
                          </TooltipContent>
                        </Tooltip>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                collapsed ? (
                  <Tooltip delayDuration={0}>
                    <TooltipTrigger asChild>
                      <SidebarMenuButton
                        onClick={() => section.href && router.push(section.href)}
                        className={cn(
                          "w-full justify-center hover:bg-accent rounded-md transition-all duration-200 ease-in-out",
                          "px-2 py-2",
                          section.href && isActive(section.href) && "bg-accent text-accent-foreground font-medium",
                        )}
                      >
                        <span className="flex items-center justify-center">
                          {React.createElement(section.icon, { className: "h-5 w-5" })}
                        </span>
                      </SidebarMenuButton>
                    </TooltipTrigger>
                    <TooltipContent side="right" className="font-medium">
                      {section.label}
                    </TooltipContent>
                  </Tooltip>
                ) : (
                  <SidebarMenuButton
                    onClick={() => section.href && router.push(section.href)}
                    className={cn(
                      "w-full justify-start hover:bg-accent rounded-md transition-all duration-200 ease-in-out",
                      "px-3 py-2",
                      section.href && isActive(section.href) && "bg-accent text-accent-foreground font-medium",
                    )}
                  >
                    <span className="mr-2">
                      {React.createElement(section.icon, { className: "h-5 w-5" })}
                    </span>
                    <span className="truncate">{section.label}</span>
                  </SidebarMenuButton>
                )
              )}
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  )
}
