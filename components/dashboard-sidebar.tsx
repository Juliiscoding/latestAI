"use client"

import type * as React from "react"
import Image from "next/image"
import { NavMain } from "@/components/nav-main"
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import { cn } from "@/lib/utils"

export function DashboardSidebar({ className, ...props }: React.ComponentProps<typeof Sidebar>) {
  const { collapsed } = useSidebar()

  return (
    <Sidebar className={cn("bg-sidebar", className)} {...props}>
      <div className="flex h-full flex-col">
        <SidebarHeader className="border-b px-4 py-2">
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg">
                <a href="#" className="flex items-center gap-2">
                  <Image
                    src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/dark-logo-2VfR0TVgVJdJYq0qetjbPKeYQsNeCI.svg"
                    alt="Mercurios.ai Logo"
                    width={collapsed ? 45 : 180}
                    height={45}
                    className="dark:brightness-200"
                  />
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>
        <SidebarContent>
          <NavMain collapsed={collapsed} />
        </SidebarContent>
      </div>
    </Sidebar>
  )
}

