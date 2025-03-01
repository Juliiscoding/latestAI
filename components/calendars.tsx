"use client"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { SidebarGroup, SidebarGroupContent, SidebarGroupLabel } from "@/components/ui/sidebar"

interface CalendarsProps {
  calendars: {
    name: string
    items: string[]
  }[]
}

export function Calendars({ calendars }: CalendarsProps) {
  return (
    <div className="space-y-4 px-2">
      {calendars.map((calendar) => (
        <SidebarGroup key={calendar.name}>
          <SidebarGroupLabel>{calendar.name}</SidebarGroupLabel>
          <SidebarGroupContent>
            <div className="space-y-2">
              {calendar.items.map((item) => (
                <div key={item} className="flex items-center space-x-2">
                  <Checkbox id={item} defaultChecked />
                  <Label htmlFor={item} className="text-sm font-normal">
                    {item}
                  </Label>
                </div>
              ))}
            </div>
          </SidebarGroupContent>
        </SidebarGroup>
      ))}
    </div>
  )
}

