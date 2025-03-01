"use client"

import * as React from "react"
import { useRouter, usePathname } from "next/navigation"
import { Home, Search, MessageSquare, Bot, BarChart, Brain, MessageCircle, Cog, ChevronDown } from "lucide-react"
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
} from "@/components/ui/sidebar"
import { cn } from "@/lib/utils"

interface NavSection {
  id: string
  icon: React.ElementType
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
      { label: "Sales Analytics", href: "/earth/sales" },
      { label: "Product & Inventory Analysis", href: "/earth/inventory" },
      { label: "Customer Analysis & Segmentation", href: "/earth/customers" },
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
                  <SidebarMenuButton
                    onClick={() => toggleSection(section.id)}
                    className={cn(
                      "w-full justify-between mb-1 hover:bg-accent rounded-md transition-all duration-200 ease-in-out",
                      collapsed ? "px-2 py-2" : "px-3 py-2",
                    )}
                  >
                    <div className="flex items-center">
                      <section.icon className={cn("h-5 w-5", collapsed ? "mx-auto" : "mr-2")} />
                      {!collapsed && (
                        <span className="truncate">
                          {section.emoji} {section.label}
                        </span>
                      )}
                    </div>
                    {!collapsed && (
                      <ChevronDown
                        className={cn(
                          "h-4 w-4 transition-transform duration-200",
                          openSections.includes(section.id) && "rotate-180",
                        )}
                      />
                    )}
                  </SidebarMenuButton>
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
                </>
              ) : (
                <SidebarMenuButton
                  onClick={() => section.href && router.push(section.href)}
                  className={cn(
                    "w-full justify-start hover:bg-accent rounded-md transition-all duration-200 ease-in-out",
                    collapsed ? "px-2 py-2" : "px-3 py-2",
                    section.href && isActive(section.href) && "bg-accent text-accent-foreground font-medium",
                  )}
                >
                  <section.icon className={cn("h-5 w-5", collapsed ? "mx-auto" : "mr-2")} />
                  {!collapsed && <span className="truncate">{section.label}</span>}
                </SidebarMenuButton>
              )}
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  )
}

