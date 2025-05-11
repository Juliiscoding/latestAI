"use client";

import React, { useState, useEffect } from "react";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { BarChart3, PieChart, LineChart, LayoutDashboard, Package, Settings, ShoppingCart, Users, CreditCard, DollarSign } from "lucide-react";
import { ResponsiveContainer, Line, LineChart as RechartsLineChart } from "recharts";
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { WarehouseProvider, useWarehouse } from '@/components/mercurios/warehouse-context';
import DashboardFilterBar from '@/components/mercurios/dashboard-filter-bar';

// Import the main Mercurios dashboard components
import StockoutRiskWidget from "@/components/mercurios/stockout-risk-widget";
import SalesTrendChart from "@/components/mercurios/sales-trend-chart";
import AIInsightsWidget from "@/components/mercurios/ai-insights-widget";
import TenantSelector from "@/components/mercurios/tenant-selector";
import TopProductsChart from "@/components/mercurios/top-products-chart";
import SalesTrendSummary from "@/components/mercurios/sales-trend-summary";
import { useTenant } from "@/lib/mercurios/tenant-context";

function ToggleRealData({ 
  useRealData, 
  setUseRealData 
}: { 
  useRealData: boolean, 
  setUseRealData: (value: boolean) => void 
}) {
  return (
    <div className="flex items-center space-x-2 mb-4 ml-auto">
      <Label htmlFor="use-real-data" className="text-sm font-medium">
        Use Real API Data
      </Label>
      <Switch
        id="use-real-data"
        checked={useRealData}
        onCheckedChange={setUseRealData}
      />
    </div>
  );
}

function BusinessIntelligenceDashboard() {
  const [useRealData, setUseRealData] = useState(false);
  const { selectedWarehouseId, selectedWarehouseName } = useWarehouse();
  const [isLoaded, setIsLoaded] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const { currentTenant } = useTenant();
  const [animationClass, setAnimationClass] = useState("opacity-0 translate-y-4");
  const [error, setError] = useState<Error | null>(null);

  // Sample data for overview charts
  const revenueData = [
    { date: "Jan", revenue: 2400 },
    { date: "Feb", revenue: 1398 },
    { date: "Mar", revenue: 9800 },
    { date: "Apr", revenue: 3908 },
    { date: "May", revenue: 4800 },
    { date: "Jun", revenue: 3800 },
    { date: "Jul", revenue: 4300 },
  ];

  const subscriptionData = [
    { date: "Jan", users: 1400 },
    { date: "Feb", users: 1800 },
    { date: "Mar", users: 2200 },
    { date: "Apr", users: 2600 },
    { date: "May", users: 2900 },
    { date: "Jun", users: 3100 },
    { date: "Jul", users: 3500 },
  ];

  const salesData = [
    { date: "Jan", sales: 4000 },
    { date: "Feb", sales: 3000 },
    { date: "Mar", sales: 5000 },
    { date: "Apr", sales: 4000 },
    { date: "May", sales: 6000 },
    { date: "Jun", sales: 5500 },
    { date: "Jul", sales: 7000 },
  ];

  useEffect(() => {
    // Add a slight delay for animations
    const timer = setTimeout(() => {
      setIsLoaded(true);
      setAnimationClass("opacity-100 translate-y-0");
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  // Error boundary
  if (error) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-2xl font-bold text-red-500 mb-4">Something went wrong</h2>
        <p className="mb-4">{error.message}</p>
        <Button onClick={() => window.location.reload()}>
          Reload Page
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 transition-all duration-300 ease-in-out p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Business Intelligence</h1>
        <div className="flex items-center space-x-2">
          <TenantSelector />
          <Button variant="outline" size="sm">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
          <ToggleRealData useRealData={useRealData} setUseRealData={setUseRealData} />
        </div>
      </div>
      
      <div className={`grid grid-cols-1 md:grid-cols-3 gap-6 transition-all duration-500 ${animationClass}`}>
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Inventory Value</CardTitle>
            <CardDescription>Current stock valuation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">€143,245.50</div>
            <p className="text-xs text-muted-foreground mt-1">
              <span className="text-emerald-500">↑ 2.5%</span> from last month
            </p>
            <div className="mt-4 h-1 bg-primary/20 rounded-full overflow-hidden">
              <div className="bg-primary h-full rounded-full" style={{ width: "65%" }}></div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Products</CardTitle>
            <CardDescription>Active inventory items</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,283</div>
            <p className="text-xs text-muted-foreground mt-1">
              <span className="text-emerald-500">↑ 12</span> new items this month
            </p>
            <div className="mt-4 grid grid-cols-4 gap-1">
              {[45, 15, 25, 15].map((value, i) => (
                <div key={i} className="flex flex-col items-center">
                  <div className="w-full bg-muted rounded-full h-12 overflow-hidden">
                    <div 
                      className="bg-primary/70 w-full rounded-t-full transition-all" 
                      style={{ height: `${value}%`, marginTop: `${100 - value}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-muted-foreground mt-1">
                    {["Q1", "Q2", "Q3", "Q4"][i]}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Stock Health</CardTitle>
            <CardDescription>Overall inventory status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">86%</div>
            <p className="text-xs text-muted-foreground mt-1">
              <span className="text-red-500">↓ 3%</span> from target level
            </p>
            <div className="mt-4 flex justify-between gap-2">
              {["Low", "Optimal", "Excess"].map((label, i) => {
                const values = [15, 65, 20];
                const colors = ["bg-red-500/70", "bg-emerald-500/70", "bg-amber-500/70"];
                return (
                  <div key={i} className="flex-1">
                    <div className="flex justify-between text-xs mb-1">
                      <span>{label}</span>
                      <span>{values[i]}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div className={`h-full ${colors[i]}`} style={{ width: `${values[i]}%` }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className={`transition-all duration-500 delay-100 ${animationClass}`}>
        <DashboardFilterBar useRealData={useRealData} />
        
        {selectedWarehouseId && (
          <div className="text-sm text-gray-500 mb-4">
            Filtered by warehouse: <span className="font-semibold">{selectedWarehouseName}</span>
          </div>
        )}
        
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="overview">
              <BarChart3 className="mr-2 h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="stockout">
              <LineChart className="mr-2 h-4 w-4" />
              Stockout Risk
            </TabsTrigger>
            <TabsTrigger value="categories">
              <PieChart className="mr-2 h-4 w-4" />
              Categories
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Card className="col-span-1">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="space-y-1">
                    <CardTitle className="text-sm font-medium">
                      Total Revenue
                    </CardTitle>
                    <CardDescription>Month to date</CardDescription>
                  </div>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">€45,231.89</div>
                  <p className="text-xs text-muted-foreground">
                    +20.1% from last month
                  </p>
                  <div className="mt-4 h-[36px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsLineChart data={revenueData}>
                        <Line
                          type="monotone"
                          strokeWidth={2}
                          dataKey="revenue"
                          activeDot={{
                            r: 6,
                            style: { fill: "var(--theme-primary)", opacity: 0.8 },
                          }}
                          style={
                            {
                              stroke: "var(--theme-primary)",
                            } as React.CSSProperties
                          }
                        />
                      </RechartsLineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
              <Card className="col-span-1">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="space-y-1">
                    <CardTitle className="text-sm font-medium">
                      Subscription
                    </CardTitle>
                    <CardDescription>Active users</CardDescription>
                  </div>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">+2350</div>
                  <p className="text-xs text-muted-foreground">
                    +180.1% from last month
                  </p>
                  <div className="mt-4 h-[36px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsLineChart data={subscriptionData}>
                        <Line
                          type="monotone"
                          strokeWidth={2}
                          dataKey="users"
                          activeDot={{
                            r: 6,
                            style: { fill: "var(--theme-primary)", opacity: 0.8 },
                          }}
                          style={
                            {
                              stroke: "var(--theme-primary)",
                            } as React.CSSProperties
                          }
                        />
                      </RechartsLineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
              <Card className="col-span-1">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="space-y-1">
                    <CardTitle className="text-sm font-medium">Sales</CardTitle>
                    <CardDescription>This month</CardDescription>
                  </div>
                  <CreditCard className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">+12,234</div>
                  <p className="text-xs text-muted-foreground">
                    +19% from last month
                  </p>
                  <div className="mt-4 h-[36px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsLineChart data={salesData}>
                        <Line
                          type="monotone"
                          strokeWidth={2}
                          dataKey="sales"
                          activeDot={{
                            r: 6,
                            style: { fill: "var(--theme-primary)", opacity: 0.8 },
                          }}
                          style={
                            {
                              stroke: "var(--theme-primary)",
                            } as React.CSSProperties
                          }
                        />
                      </RechartsLineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <div className="grid gap-4 grid-cols-1 md:grid-cols-3">
              <ErrorBoundary fallback={<Card className="p-4">Sales trend data unavailable</Card>}>
                <SalesTrendSummary 
                  useRealData={useRealData} 
                  warehouseId={selectedWarehouseId}
                />
              </ErrorBoundary>
              <ErrorBoundary fallback={<Card className="p-4">Top products data unavailable</Card>}>
                <TopProductsChart 
                  useRealData={useRealData} 
                  warehouseId={selectedWarehouseId} 
                />
              </ErrorBoundary>
            </div>
            
            <div className="grid gap-4 grid-cols-1">
              <ErrorBoundary fallback={<Card className="p-4">Sales trend chart unavailable</Card>}>
                <SalesTrendChart />
              </ErrorBoundary>
            </div>
          </TabsContent>
          
          <TabsContent value="stockout" className="space-y-4">
            <ErrorBoundary fallback={<Card className="p-4">Stockout risk data unavailable</Card>}>
              <StockoutRiskWidget 
                warehouseId={selectedWarehouseId}
              />
            </ErrorBoundary>
            <ErrorBoundary fallback={<Card className="p-4">AI insights unavailable</Card>}>
              <AIInsightsWidget 
                useRealData={useRealData}
                warehouseId={selectedWarehouseId}
              />
            </ErrorBoundary>
          </TabsContent>
          
          <TabsContent value="categories" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Product Categories</CardTitle>
                <CardDescription>
                  Distribution of products across categories
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px] flex items-center justify-center bg-muted/50 rounded">
                  <div className="text-center">
                    <PieChart className="h-10 w-10 mx-auto text-primary opacity-50" />
                    <p className="text-muted-foreground mt-2">
                      Category distribution chart will be displayed here
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// Simple ErrorBoundary component
class ErrorBoundary extends React.Component<{
  children: React.ReactNode;
  fallback: React.ReactNode;
}> {
  state = { hasError: false };
  
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  
  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    
    return this.props.children;
  }
}

export default function BusinessIntelligencePage() {
  return (
    <WarehouseProvider>
      <ErrorBoundary fallback={<Card className="p-4">Business Intelligence dashboard unavailable</Card>}>
        <BusinessIntelligenceDashboard />
      </ErrorBoundary>
    </WarehouseProvider>
  );
}
