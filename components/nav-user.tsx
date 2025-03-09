"use client"
import { BadgeCheck, Bell, ChevronsUpDown, CreditCard, LogOut, Sparkles } from "lucide-react"
import { useRouter } from "next/navigation"
import Link from "next/link"

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
  const router = useRouter()
  
  const handleLogout = async () => {
    try {
      // Call the logout API endpoint to clear the auth cookie server-side
      await fetch('/api/logout', {
        method: 'GET',
        credentials: 'include'
      })
      
      // Also clear client-side cookie for immediate effect
      document.cookie = "auth=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;"
      
      // Redirect to homepage
      window.location.href = "/"
    } catch (error) {
      console.error('Logout error:', error)
      // Fallback: still try to redirect even if API call fails
      window.location.href = "/"
    }
  }

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
        <Link href="/account" passHref>
          <DropdownMenuItem className="gap-2 text-foreground focus:text-accent-foreground focus:bg-accent cursor-pointer">
            <BadgeCheck className="h-4 w-4" />
            Account
          </DropdownMenuItem>
        </Link>
        <Link href="/billing" passHref>
          <DropdownMenuItem className="gap-2 text-foreground focus:text-accent-foreground focus:bg-accent cursor-pointer">
            <CreditCard className="h-4 w-4" />
            Billing
          </DropdownMenuItem>
        </Link>
        <Link href="/notifications" passHref>
          <DropdownMenuItem className="gap-2 text-foreground focus:text-accent-foreground focus:bg-accent cursor-pointer">
            <Bell className="h-4 w-4" />
            Notifications
          </DropdownMenuItem>
        </Link>
        <DropdownMenuSeparator className="-mx-2 my-2 bg-border" />
        <DropdownMenuItem 
          className="gap-2 text-foreground focus:text-accent-foreground focus:bg-accent cursor-pointer"
          onClick={handleLogout}
        >
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

