"use client"
import { BadgeCheck, Bell, ChevronsUpDown, CreditCard, LogOut, Sparkles } from "lucide-react"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useSidebar } from "@/components/ui/sidebar"
import { cn } from "@/lib/utils"

export function NavUser({
  user,
}: {
  user: {
    name: string
    email: string
    avatar: string
  }
}) {
  const { isMobile } = useSidebar()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <div
          className={cn(
            "flex items-center gap-2 rounded-lg p-2 text-sm font-medium hover:bg-muted cursor-pointer",
            "data-[state=open]:bg-accent data-[state=open]:text-accent-foreground",
          )}
        >
          <Avatar className="h-8 w-8 rounded-lg">
            <AvatarImage src={user.avatar} alt={user.name} />
            <AvatarFallback className="rounded-lg">SC</AvatarFallback>
          </Avatar>
          <div className="grid text-left text-sm leading-tight">
            <span className="font-semibold">{user.name}</span>
            <span className="text-xs text-muted-foreground">{user.email}</span>
          </div>
          <ChevronsUpDown className="ml-2 h-4 w-4" />
        </div>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg p-2 bg-background border shadow-lg"
        align="end"
        sideOffset={4}
      >
        <div className="flex items-center gap-2 px-2 py-1.5 bg-popover">
          <Avatar className="h-8 w-8 rounded-lg">
            <AvatarImage src={user.avatar} alt={user.name} />
            <AvatarFallback className="rounded-lg">SC</AvatarFallback>
          </Avatar>
          <div className="grid flex-1">
            <span className="text-sm font-semibold text-foreground">{user.name}</span>
            <span className="text-xs text-muted-foreground">{user.email}</span>
          </div>
        </div>
        <DropdownMenuSeparator className="-mx-2 my-2 bg-border" />
        <DropdownMenuItem className="gap-2 text-foreground focus:text-accent-foreground focus:bg-accent">
          <Sparkles className="h-4 w-4" />
          Upgrade to Pro
        </DropdownMenuItem>
        <DropdownMenuSeparator className="-mx-2 my-2 bg-border" />
        <DropdownMenuItem className="gap-2 text-foreground focus:text-accent-foreground focus:bg-accent">
          <BadgeCheck className="h-4 w-4" />
          Account
        </DropdownMenuItem>
        <DropdownMenuItem className="gap-2 text-foreground focus:text-accent-foreground focus:bg-accent">
          <CreditCard className="h-4 w-4" />
          Billing
        </DropdownMenuItem>
        <DropdownMenuItem className="gap-2 text-foreground focus:text-accent-foreground focus:bg-accent">
          <Bell className="h-4 w-4" />
          Notifications
        </DropdownMenuItem>
        <DropdownMenuSeparator className="-mx-2 my-2 bg-border" />
        <DropdownMenuItem className="gap-2 text-foreground focus:text-accent-foreground focus:bg-accent">
          <LogOut className="h-4 w-4" />
          Log out
        </DropdownMenuItem>
        <style jsx global>{`
          .dropdown-menu-content {
            background-color: hsl(var(--background));
            color: hsl(var(--foreground));
          }
          .dropdown-menu-content * {
            opacity: 1 !important;
          }
        `}</style>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

