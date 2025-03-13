/**
 * Earth Module Shadcn Charts
 * 
 * This file implements chart components for the Earth module using the shadcn/ui chart library.
 * These components provide beautiful, interactive visualizations for Snowflake analytics data.
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Button } from "./components/ui/button";
import { Badge } from "./components/ui/badge";
import { 
  AreaChart, 
  BarChart, 
  LineChart, 
  PieChart,
  DonutChart,
  RadarChart,
  RadialBarChart,
} from "./components/ui/charts";
import { ArrowUpIcon, ArrowDownIcon, CalendarIcon, DownloadIcon } from "lucide-react";

/**
 * Chart Card Component
 * 
 * A wrapper component for charts that provides a consistent card layout with title,
 * description, trend indicator, and optional actions.
 */
export const ChartCard = ({ 
  title, 
  description, 
  children, 
  trend = null, 
  period = "January - June 2024",
  actions = null,
  className = "",
}) => {
  // Format trend percentage
  const trendValue = trend ? Math.abs(trend).toFixed(1) : null;
  const trendDirection = trend >= 0 ? "up" : "down";
  
  return (
    <Card className={`shadow-sm ${className}`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-medium">{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          {actions && (
            <div className="flex space-x-2">
              {actions}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {children}
      </CardContent>
      {(trend || period) && (
        <CardFooter className="pt-0 flex justify-between items-center text-sm text-muted-foreground">
          {trend && (
            <div className="flex items-center">
              <span className={`inline-flex items-center mr-1 ${trendDirection === 'up' ? 'text-emerald-500' : 'text-rose-500'}`}>
                {trendDirection === 'up' ? <ArrowUpIcon className="h-3 w-3 mr-1" /> : <ArrowDownIcon className="h-3 w-3 mr-1" />}
                {trendValue}%
              </span>
              <span>Trending {trendDirection} this month</span>
            </div>
          )}
          {period && (
            <div className="flex items-center">
              <CalendarIcon className="h-3 w-3 mr-1" />
              <span>{period}</span>
            </div>
          )}
        </CardFooter>
      )}
    </Card>
  );
};

/**
 * Sales Trend Chart
 * 
 * Displays sales trend data with options to view as line, area, or bar chart.
 */
export const SalesTrendChart = ({ data, title = "Sales Trend", description = "Showing total sales for the last 6 months" }) => {
  return (
    <Tabs defaultValue="line">
      <ChartCard 
        title={title} 
        description={description}
        trend={5.2}
        actions={
          <TabsList>
            <TabsTrigger value="line">Line</TabsTrigger>
            <TabsTrigger value="area">Area</TabsTrigger>
            <TabsTrigger value="bar">Bar</TabsTrigger>
          </TabsList>
        }
      >
        <div className="h-[300px]">
          <TabsContent value="line" className="mt-0">
            <LineChart
              data={data}
              categories={["sales"]}
              index="date"
              colors={["blue"]}
              valueFormatter={(value) => `$${value.toLocaleString()}`}
              showLegend={false}
              showGridLines={true}
              showAnimation={true}
              className="h-[300px]"
            />
          </TabsContent>
          <TabsContent value="area" className="mt-0">
            <AreaChart
              data={data}
              categories={["sales"]}
              index="date"
              colors={["blue"]}
              valueFormatter={(value) => `$${value.toLocaleString()}`}
              showLegend={false}
              showGridLines={true}
              showAnimation={true}
              className="h-[300px]"
            />
          </TabsContent>
          <TabsContent value="bar" className="mt-0">
            <BarChart
              data={data}
              categories={["sales"]}
              index="date"
              colors={["blue"]}
              valueFormatter={(value) => `$${value.toLocaleString()}`}
              showLegend={false}
              showGridLines={true}
              showAnimation={true}
              className="h-[300px]"
            />
          </TabsContent>
        </div>
      </ChartCard>
    </Tabs>
  );
};

/**
 * Sales Comparison Chart
 * 
 * Compares sales data across multiple categories or time periods.
 */
export const SalesComparisonChart = ({ 
  data, 
  categories = ["current", "previous"],
  title = "Sales Comparison", 
  description = "Comparing current vs previous period" 
}) => {
  return (
    <ChartCard 
      title={title} 
      description={description}
      trend={5.2}
    >
      <div className="h-[300px]">
        <BarChart
          data={data}
          categories={categories}
          index="date"
          colors={["blue", "sky"]}
          valueFormatter={(value) => `$${value.toLocaleString()}`}
          showLegend={true}
          showGridLines={true}
          showAnimation={true}
          className="h-[300px]"
        />
      </div>
    </ChartCard>
  );
};

/**
 * Customer Distribution Chart
 * 
 * Displays customer distribution by segment, region, or other categories.
 */
export const CustomerDistributionChart = ({ 
  data, 
  title = "Customer Distribution", 
  description = "Distribution by customer segment" 
}) => {
  return (
    <Tabs defaultValue="pie">
      <ChartCard 
        title={title} 
        description={description}
        actions={
          <TabsList>
            <TabsTrigger value="pie">Pie</TabsTrigger>
            <TabsTrigger value="donut">Donut</TabsTrigger>
          </TabsList>
        }
      >
        <div className="h-[300px]">
          <TabsContent value="pie" className="mt-0">
            <PieChart
              data={data}
              category="value"
              index="name"
              valueFormatter={(value) => `${value.toLocaleString()}`}
              showAnimation={true}
              className="h-[300px]"
            />
          </TabsContent>
          <TabsContent value="donut" className="mt-0">
            <DonutChart
              data={data}
              category="value"
              index="name"
              valueFormatter={(value) => `${value.toLocaleString()}`}
              showAnimation={true}
              className="h-[300px]"
            />
          </TabsContent>
        </div>
      </ChartCard>
    </Tabs>
  );
};

/**
 * Product Performance Radar Chart
 * 
 * Visualizes product performance across multiple dimensions.
 */
export const ProductPerformanceRadarChart = ({ 
  data, 
  title = "Product Performance", 
  description = "Performance across key metrics" 
}) => {
  return (
    <Tabs defaultValue="filled">
      <ChartCard 
        title={title} 
        description={description}
        actions={
          <TabsList>
            <TabsTrigger value="filled">Filled</TabsTrigger>
            <TabsTrigger value="dots">Dots</TabsTrigger>
            <TabsTrigger value="lines">Lines</TabsTrigger>
          </TabsList>
        }
      >
        <div className="h-[300px]">
          <TabsContent value="filled" className="mt-0">
            <RadarChart
              data={data}
              categories={["value"]}
              index="metric"
              colors={["blue"]}
              valueFormatter={(value) => `${value.toLocaleString()}`}
              showAnimation={true}
              className="h-[300px]"
              variant="filled"
            />
          </TabsContent>
          <TabsContent value="dots" className="mt-0">
            <RadarChart
              data={data}
              categories={["value"]}
              index="metric"
              colors={["blue"]}
              valueFormatter={(value) => `${value.toLocaleString()}`}
              showAnimation={true}
              className="h-[300px]"
              variant="dots"
            />
          </TabsContent>
          <TabsContent value="lines" className="mt-0">
            <RadarChart
              data={data}
              categories={["value"]}
              index="metric"
              colors={["blue"]}
              valueFormatter={(value) => `${value.toLocaleString()}`}
              showAnimation={true}
              className="h-[300px]"
              variant="lines"
            />
          </TabsContent>
        </div>
      </ChartCard>
    </Tabs>
  );
};

/**
 * Multi-Product Performance Radar Chart
 * 
 * Compares multiple products across performance dimensions.
 */
export const MultiProductRadarChart = ({ 
  data, 
  categories,
  title = "Product Comparison", 
  description = "Comparing products across key metrics" 
}) => {
  return (
    <ChartCard 
      title={title} 
      description={description}
    >
      <div className="h-[300px]">
        <RadarChart
          data={data}
          categories={categories}
          index="metric"
          valueFormatter={(value) => `${value.toLocaleString()}`}
          showAnimation={true}
          className="h-[300px]"
        />
      </div>
    </ChartCard>
  );
};

/**
 * Metric Gauge Chart
 * 
 * Displays a single metric as a gauge chart.
 */
export const MetricGaugeChart = ({ 
  value, 
  title = "Metric", 
  description = "Key performance indicator",
  maxValue = 100,
  unit = "",
  trend = null,
}) => {
  // Calculate percentage for the gauge
  const percentage = (value / maxValue) * 100;
  
  // Format display value
  const displayValue = unit 
    ? (unit === "$" ? `${unit}${value.toLocaleString()}` : `${value.toLocaleString()}${unit}`)
    : value.toLocaleString();
  
  return (
    <ChartCard 
      title={title} 
      description={description}
      trend={trend}
    >
      <div className="h-[200px] flex items-center justify-center">
        <RadialBarChart
          data={[{ name: "Value", value: percentage }]}
          category="value"
          index="name"
          showAnimation={true}
          showLegend={false}
          className="h-[200px]"
        >
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-3xl font-bold">{displayValue}</div>
              <div className="text-sm text-muted-foreground">{title}</div>
            </div>
          </div>
        </RadialBarChart>
      </div>
    </ChartCard>
  );
};

/**
 * Interactive Daily Sales Chart
 * 
 * Displays daily sales data with interactive tooltips.
 */
export const InteractiveDailySalesChart = ({ 
  data, 
  title = "Daily Sales", 
  description = "Showing daily sales for the last 3 months",
  summaryData = null,
}) => {
  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-medium">{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          <Button variant="outline" size="sm">
            <DownloadIcon className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </CardHeader>
      
      {summaryData && (
        <div className="grid grid-cols-2 gap-4 px-6">
          {Object.entries(summaryData).map(([key, value]) => (
            <div key={key} className="text-center p-2">
              <div className="text-2xl font-bold">{value.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">{key}</div>
            </div>
          ))}
        </div>
      )}
      
      <CardContent>
        <div className="h-[300px]">
          <BarChart
            data={data}
            categories={["sales"]}
            index="date"
            colors={["blue"]}
            valueFormatter={(value) => `$${value.toLocaleString()}`}
            showLegend={false}
            showGridLines={true}
            showAnimation={true}
            className="h-[300px]"
            showTooltip={true}
            showXAxis={true}
            showYAxis={true}
          />
        </div>
      </CardContent>
      
      <CardFooter className="pt-0 flex justify-between items-center text-sm text-muted-foreground">
        <div className="flex items-center">
          <ArrowUpIcon className="h-3 w-3 mr-1 text-emerald-500" />
          <span className="text-emerald-500 mr-1">5.2%</span>
          <span>Trending up this month</span>
        </div>
        <div className="flex items-center">
          <CalendarIcon className="h-3 w-3 mr-1" />
          <span>April - June 2024</span>
        </div>
      </CardFooter>
    </Card>
  );
};

/**
 * Multi-Metric Dashboard Card
 * 
 * Displays multiple metrics in a single card with a chart.
 */
export const MultiMetricDashboardCard = ({ 
  metrics, 
  chartData, 
  title = "Performance Overview", 
  description = "Key metrics at a glance" 
}) => {
  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-6 border-t border-b">
        {metrics.map((metric, index) => (
          <div key={index} className="text-center">
            <div className="text-sm text-muted-foreground mb-1">{metric.label}</div>
            <div className="text-2xl font-bold">{metric.value}</div>
            {metric.change && (
              <div className={`text-xs flex items-center justify-center mt-1 ${metric.change >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                {metric.change >= 0 
                  ? <ArrowUpIcon className="h-3 w-3 mr-1" /> 
                  : <ArrowDownIcon className="h-3 w-3 mr-1" />}
                {Math.abs(metric.change)}%
              </div>
            )}
          </div>
        ))}
      </div>
      
      <CardContent>
        <div className="h-[200px]">
          <LineChart
            data={chartData}
            categories={["value"]}
            index="date"
            colors={["blue"]}
            valueFormatter={(value) => `${value.toLocaleString()}`}
            showLegend={false}
            showGridLines={true}
            showAnimation={true}
            className="h-[200px]"
          />
        </div>
      </CardContent>
    </Card>
  );
};
