"use client"

import * as React from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const days = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

export function DatePicker() {
  const [currentDate, setCurrentDate] = React.useState(new Date())

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate()

  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay()

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.setMonth(currentDate.getMonth() - 1)))
  }

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.setMonth(currentDate.getMonth() + 1)))
  }

  return (
    <div className="p-4">
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
            <Button
              key={day}
              variant="ghost"
              className={cn(
                "h-8 w-8 p-0 hover:bg-accent",
                isToday && "bg-primary text-primary-foreground hover:bg-primary/90",
              )}
            >
              {day}
            </Button>
          )
        })}
      </div>
    </div>
  )
}

