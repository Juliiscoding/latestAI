'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from 'recharts';
import { Loader2, Download, ArrowUpDown } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';
import { useTopProducts } from '@/lib/hooks/use-top-products';

interface TopProductsChartProps {
  className?: string;
  limit?: number;
  useRealData?: boolean;
  warehouseId?: string | null;
}

export default function TopProductsChart({ 
  className, 
  limit = 5, 
  useRealData = false,
  warehouseId = null
}: TopProductsChartProps) {
  const [period, setPeriod] = useState<'7days' | '30days' | '90days'>('30days');
  const [sortBy, setSortBy] = useState<'quantity' | 'revenue'>('revenue');
  const [realData, setRealData] = useState(useRealData);

  // Use our custom hook to fetch top products data
  const { data, isLoading, error, refetch } = useTopProducts(period, sortBy, limit, { useRealData: realData, warehouseId });

  // Colors for chart bars
  const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#6366f1', '#ec4899'];

  const handlePeriodChange = (value: string) => {
    setPeriod(value as '7days' | '30days' | '90days');
  };

  const handleSortByChange = (value: string) => {
    setSortBy(value as 'quantity' | 'revenue');
  };

  // Format data for the chart
  const formatChartData = () => {
    if (!data?.products) return [];

    return data.products.map((product) => ({
      name: product.name.length > 18 ? product.name.slice(0, 18) + '...' : product.name, 
      value: sortBy === 'revenue' ? product.revenue : product.quantity,
      fullName: product.name,
      category: product.category,
      percentageOfTotal: product.percentageOfTotal.toFixed(1),
      originalValue: sortBy === 'revenue' 
        ? formatCurrency(product.revenue) 
        : product.quantity.toLocaleString()
    }));
  };

  // Function to export data as CSV
  const exportToCSV = () => {
    if (!data?.products || data.products.length === 0) return;
    
    // Create CSV content
    const headers = ['Product', 'Category', 'Quantity', 'Revenue', '% of Total'];
    const csvContent = [
      headers.join(','),
      ...data.products.map(product => 
        `"${product.name}","${product.category}",${product.quantity.toLocaleString()},${formatCurrency(product.revenue)},${product.percentageOfTotal.toFixed(1)}%`
      )
    ].join('\n');
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `top-products-${period}-${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Custom tooltip for the chart
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-background border rounded-md shadow-md p-3 text-sm">
          <p className="font-medium">{data.fullName}</p>
          <p className="text-muted-foreground">Category: {data.category}</p>
          <p className="mt-1">
            {sortBy === 'revenue' ? 'Revenue: ' : 'Quantity: '}
            <span className="font-medium">{data.originalValue}</span>
          </p>
          <p className="text-xs mt-1">
            {data.percentageOfTotal}% of total
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="space-y-1">
          <CardTitle className="text-xl">Top Products</CardTitle>
          <CardDescription>
            Best performing products by {sortBy === 'revenue' ? 'revenue' : 'units sold'}
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
          
          <Select value={sortBy} onValueChange={handleSortByChange}>
            <SelectTrigger className="w-[110px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="revenue">Revenue</SelectItem>
              <SelectItem value="quantity">Quantity</SelectItem>
            </SelectContent>
          </Select>
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setRealData(!realData)}
          >
            {realData ? 'Use Mock' : 'Use Real'}
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            Refresh
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={exportToCSV}
          >
            <Download className="w-4 h-4 mr-2" />
            CSV
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center items-center h-[400px]">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="h-[400px] flex flex-col justify-center items-center">
            <p className="text-destructive mb-2">Error loading product data</p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              Try Again
            </Button>
          </div>
        ) : (
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={formatChartData()}
                margin={{ top: 10, right: 30, left: 80, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                <XAxis 
                  type="number" 
                  tickFormatter={(value) => sortBy === 'revenue' 
                    ? formatCurrency(value, true) 
                    : value.toLocaleString()
                  } 
                />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  width={80}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar 
                  dataKey="value" 
                  background={{ fill: '#f9fafb' }}
                  radius={[0, 4, 4, 0]}
                >
                  {formatChartData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        
        {data && !isLoading && !error && (
          <div className="mt-4 text-sm text-muted-foreground grid grid-cols-2 gap-4">
            <div>
              <span className="block">Total {sortBy === 'revenue' ? 'Revenue' : 'Units'}: </span>
              <span className="font-medium text-base">
                {sortBy === 'revenue' 
                  ? formatCurrency(data.totalRevenue) 
                  : data.totalQuantity.toLocaleString()
                }
              </span>
            </div>
            <div className="text-right">
              <span className="block">Period: </span>
              <span className="font-medium text-base">
                {new Date(data.startDate).toLocaleDateString()} — {new Date(data.endDate).toLocaleDateString()}
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
