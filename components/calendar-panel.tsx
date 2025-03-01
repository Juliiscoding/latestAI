"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

const days = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

export function CalendarPanel() {
  const [currentDate, setCurrentDate] = useState(new Date())

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate()

  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay()

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.setMonth(currentDate.getMonth() - 1)))
  }

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.setMonth(currentDate.getMonth() + 1)))
  }

  return (
    <Card className="w-[300px] border-l">
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <img
              src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Screenshot%202025-02-12%20at%2014.15.48-kzFiq1EPn4wVGQidxSJPRfPEc8YBOW.png"
              alt="User Avatar"
              className="w-8 h-8 rounded-full mr-2"
            />
            <div>
              <div className="font-semibold">shadcn</div>
              <div className="text-sm text-muted-foreground">m@example.com</div>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between mb-4">
          <button onClick={prevMonth} className="p-1">
            <ChevronLeft className="h-4 w-4" />
          </button>
          <div className="font-medium">
            {currentDate.toLocaleString("default", {
              month: "long",
              year: "numeric",
            })}
          </div>
          <button onClick={nextMonth} className="p-1">
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>

        <div className="grid grid-cols-7 gap-1 text-center text-sm mb-2">
          {days.map((day) => (
            <div key={day} className="text-muted-foreground">
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1 text-center">
          {Array.from({ length: firstDayOfMonth }).map((_, index) => (
            <div key={`empty-${index}`} />
          ))}
          {Array.from({ length: daysInMonth }).map((_, index) => {
            const day = index + 1
            const isToday =
              day === new Date().getDate() &&
              currentDate.getMonth() === new Date().getMonth() &&
              currentDate.getFullYear() === new Date().getFullYear()

            return (
              <button
                key={day}
                className={cn(
                  "aspect-square p-1 hover:bg-accent rounded-md",
                  isToday && "bg-primary text-primary-foreground hover:bg-primary/90",
                )}
              >
                {day}
              </button>
            )
          })}
        </div>

        <div className="mt-4 space-y-4">
          <div>
            <h3 className="font-medium mb-2">My Calendars</h3>
            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>Personal</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>Work</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="checkbox" className="rounded" />
                <span>Family</span>
              </label>
            </div>
          </div>

          <div>
            <h3 className="font-medium mb-2">Favorites</h3>
            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>Holidays</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>Birthdays</span>
              </label>
            </div>
          </div>

          <div>
            <h3 className="font-medium mb-2">Other</h3>
            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>Travel</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>Reminders</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="checkbox" className="rounded" />
                <span>Deadlines</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}

