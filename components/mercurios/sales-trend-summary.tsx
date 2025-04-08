'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Loader2, TrendingUp, TrendingDown, DollarSign, ShoppingCart } from 'lucide-react';
import { useSalesTrend } from '@/lib/hooks/use-top-products';
import { formatCurrency } from '@/lib/utils';
import { cn } from '@/lib/utils';

export interface SalesTrendSummaryProps {
  className?: string;
  useRealData?: boolean;
  warehouseId?: string | null;
}

export default function SalesTrendSummary({ 
  className = '',
  useRealData = false,
  warehouseId = null
}: SalesTrendSummaryProps) {
  const [period, setPeriod] = useState<'7days' | '30days' | '90days'>('30days');

  // Use our custom hook to fetch sales trend data
  const { data, isLoading, error, refetch } = useSalesTrend(period, { 
    useRealData,
    warehouseId
  });

  const handlePeriodChange = (value: string) => {
    setPeriod(value as '7days' | '30days' | '90days');
  };

  const handleDataToggle = () => {
    useRealData = !useRealData;
  };

  // Get trend message and emoji based on percent change
  const getTrendMessage = (percentChange: number, metricName: string) => {
    if (percentChange > 20) {
      return `🚀 ${metricName} are skyrocketing up ${percentChange.toFixed(1)}%!`;
    } else if (percentChange > 5) {
      return `🟢 ${metricName} are up ${percentChange.toFixed(1)}% vs previous ${data?.periodName}.`;
    } else if (percentChange > 0) {
      return `📈 ${metricName} are slightly up ${percentChange.toFixed(1)}%.`;
    } else if (percentChange > -5) {
      return `📉 ${metricName} are slightly down ${Math.abs(percentChange).toFixed(1)}%.`;
    } else if (percentChange > -20) {
      return `🔴 ${metricName} are down ${Math.abs(percentChange).toFixed(1)}% vs previous ${data?.periodName}.`;
    } else {
      return `⚠️ ${metricName} have dropped ${Math.abs(percentChange).toFixed(1)}%! Time to investigate.`;
    }
  };

  // Get humorous message based on trend
  const getHumorousMessage = (revenueChange: number, orderChange: number) => {
    if (revenueChange > 15 && orderChange > 15) {
      return "Time to pop the champagne! 🍾";
    } else if (revenueChange > 5 && orderChange > 5) {
      return "Looking good! Maybe order lunch for the team? 🥪";
    } else if (revenueChange > 0 && orderChange > 0) {
      return "Slow but steady growth. We'll take it! 👍";
    } else if (revenueChange < 0 && orderChange < 0) {
      if (revenueChange < -15) {
        return "Have you tried sacrificing a product manager? 🔮";
      } else {
        return "Maybe skip the team lunch today... 🥲";
      }
    } else if (revenueChange > 0 && orderChange < 0) {
      return "Fewer orders but higher value. Upselling works! 💰";
    } else {
      return "More orders but less revenue? Check your discount strategy! 🤔";
    }
  };

  // Get trend icon and color
  const getTrendIcon = (percentChange: number) => {
    if (percentChange > 0) {
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    } else {
      return <TrendingDown className="h-4 w-4 text-red-500" />;
    }
  };

  // Get badge style based on percent change
  const getBadgeVariant = (percentChange: number) => {
    if (percentChange > 10) return "success";
    if (percentChange > 0) return "outline";
    if (percentChange > -10) return "secondary";
    return "destructive";
  };

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="space-y-1">
          <CardTitle className="text-xl">Sales Trend</CardTitle>
          <CardDescription>
            Performance analysis vs previous period
          </CardDescription>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Select value={period} onValueChange={handlePeriodChange}>
            <SelectTrigger className="w-[110px]">
              <SelectValue placeholder="Period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7days">7 Days</SelectItem>
              <SelectItem value="30days">30 Days</SelectItem>
              <SelectItem value="90days">90 Days</SelectItem>
            </SelectContent>
          </Select>
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleDataToggle}
          >
            {useRealData ? 'Use Mock' : 'Use Real'}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center items-center h-[180px]">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="h-[180px] flex flex-col justify-center items-center">
            <p className="text-destructive mb-2">Error loading trend data</p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              Try Again
            </Button>
          </div>
        ) : data ? (
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h3 className="font-medium flex items-center">
                  <DollarSign className="h-4 w-4 mr-1" />
                  Revenue
                </h3>
                <Badge 
                  variant={getBadgeVariant(data.changes.revenue) as any}
                  className="flex items-center gap-1"
                >
                  {getTrendIcon(data.changes.revenue)}
                  {data.changes.revenue > 0 ? '+' : ''}{data.changes.revenue.toFixed(1)}%
                </Badge>
              </div>
              <p className={cn(
                "text-sm",
                data.changes.revenue > 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
              )}>
                {getTrendMessage(data.changes.revenue, 'Sales')}
              </p>
              <div className="flex justify-between mt-1 text-xs text-muted-foreground">
                <div>
                  Current: <span className="font-medium">{formatCurrency(data.currentPeriod.totalRevenue)}</span>
                </div>
                <div>
                  Previous: <span className="font-medium">{formatCurrency(data.previousPeriod.totalRevenue)}</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h3 className="font-medium flex items-center">
                  <ShoppingCart className="h-4 w-4 mr-1" />
                  Orders
                </h3>
                <Badge 
                  variant={getBadgeVariant(data.changes.orderCount) as any}
                  className="flex items-center gap-1"
                >
                  {getTrendIcon(data.changes.orderCount)}
                  {data.changes.orderCount > 0 ? '+' : ''}{data.changes.orderCount.toFixed(1)}%
                </Badge>
              </div>
              <p className={cn(
                "text-sm",
                data.changes.orderCount > 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
              )}>
                {getTrendMessage(data.changes.orderCount, 'Orders')}
              </p>
              <div className="flex justify-between mt-1 text-xs text-muted-foreground">
                <div>
                  Current: <span className="font-medium">{data.currentPeriod.orderCount.toLocaleString()}</span>
                </div>
                <div>
                  Previous: <span className="font-medium">{data.previousPeriod.orderCount.toLocaleString()}</span>
                </div>
              </div>
            </div>
            
            <div className="border-t pt-4 mt-4">
              <p className="text-center italic text-sm">
                {getHumorousMessage(data.changes.revenue, data.changes.orderCount)}
              </p>
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
