"use client"

import * as React from "react"
import { Bar, BarChart as RechartsBarChart, CartesianGrid, XAxis } from "recharts"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { type ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

const chartData = [
  { date: "2024-04-01", desktop: 222, mobile: 150 },
  { date: "2024-04-02", desktop: 97, mobile: 180 },
  { date: "2024-04-03", desktop: 167, mobile: 120 },
  { date: "2024-04-04", desktop: 242, mobile: 260 },
  { date: "2024-04-05", desktop: 373, mobile: 290 },
  { date: "2024-04-06", desktop: 301, mobile: 340 },
  { date: "2024-04-07", desktop: 245, mobile: 180 },
]

const chartConfig = {
  views: {
    label: "Sales Channels",
    color: "#000000", // Adding default color to fix TypeScript error
  },
  desktop: {
    label: "Online",
    color: "#1A263B",
  },
  mobile: {
    label: "In-Store",
    color: "#6ACBDF",
  },
} satisfies ChartConfig

export function BarChart() {
  const [activeChart, setActiveChart] = React.useState<keyof typeof chartConfig>("desktop")

  const total = React.useMemo(
    () => ({
      desktop: chartData.reduce((acc, curr) => acc + curr.desktop, 0),
      mobile: chartData.reduce((acc, curr) => acc + curr.mobile, 0),
    }),
    [],
  )

  return (
    <Card className="bg-white">
      <CardHeader className="flex flex-col items-stretch space-y-0 border-b p-0 lg:flex-row">
        <div className="flex flex-1 flex-col justify-center gap-1 px-4 py-4 sm:px-6 sm:py-5 lg:py-6">
          <CardTitle className="text-gray-800 text-base sm:text-lg">Sales Channels</CardTitle>
          <CardDescription className="text-gray-600 text-xs sm:text-sm">Online vs In-Store Sales</CardDescription>
        </div>
        <div className="grid grid-cols-2 w-full max-w-full sm:max-w-[280px] lg:max-w-[320px]">
          {["desktop", "mobile"].map((key) => {
            const chart = key as keyof typeof chartConfig
            return (
              <button
                key={chart}
                data-active={activeChart === chart}
                className="relative z-30 flex flex-col justify-center gap-0.5 sm:gap-1 border-t px-2 py-3 text-left even:border-l data-[active=true]:bg-mercurios-lightGray sm:border-l sm:border-t-0 sm:px-3 md:px-4 lg:px-6 sm:py-4 lg:py-6"
                onClick={() => setActiveChart(chart)}
              >
                <span className="text-[10px] sm:text-xs text-mercurios-darkBlue whitespace-nowrap">{chartConfig[chart].label}</span>
                <span className="text-base sm:text-lg md:text-xl lg:text-2xl font-bold leading-none text-mercurios-darkBlue whitespace-nowrap overflow-hidden text-ellipsis">
                  €{total[key as keyof typeof total].toLocaleString()}
                </span>
              </button>
            )
          })}
        </div>
      </CardHeader>
      <CardContent className="px-1 py-2 sm:p-4 md:p-6">
        <ChartContainer config={chartConfig} className="aspect-auto h-[200px] sm:h-[220px] md:h-[250px] w-full">
          <RechartsBarChart
            data={chartData}
            margin={{
              left: 8,
              right: 8,
              top: 8,
              bottom: 8
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={4}
              minTickGap={16}
              tick={{ fontSize: 10 }}
              tickFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })
              }}
            />
            <ChartTooltip
              content={
                <ChartTooltipContent
                  className="w-[120px] sm:w-[150px]"
                  nameKey="views"
                  labelFormatter={(value) => {
                    return new Date(value).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })
                  }}
                />
              }
            />
            <Bar dataKey={activeChart} fill={chartConfig[activeChart].color} />
          </RechartsBarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

