'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Loader2, Calendar, Download } from 'lucide-react';
import { useSalesTrend } from '@/lib/hooks/use-prohandel-data';

interface SalesTrendProps {
  period?: '7days' | '30days' | '90days' | 'year';
}

export default function SalesTrendChart({ period = '30days' }: SalesTrendProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<'7days' | '30days' | '90days' | 'year'>(period);
  const [useRealData, setUseRealData] = useState(false);

  // Use our custom hook for data fetching
  const { data, isLoading, error, refetch } = useSalesTrend(selectedPeriod, { useRealData });

  const handlePeriodChange = (value: string) => {
    setSelectedPeriod(value as '7days' | '30days' | '90days' | 'year');
  };

  const handleDataToggle = () => {
    setUseRealData(!useRealData);
  };

  // Function to export data as CSV
  const exportToCSV = () => {
    if (!data || data.length === 0) return;
    
    // Create CSV content
    const headers = ['Date', 'Sales (€)', 'Orders'];
    const csvContent = [
      headers.join(','),
      ...data.map(item => `${item.date},${item.sales},${item.orders}`)
    ].join('\n');
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `sales-trend-${selectedPeriod}-${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Sales Trend</CardTitle>
          <CardDescription>Revenue performance over time</CardDescription>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-4">
            <Select value={selectedPeriod} onValueChange={handlePeriodChange}>
              <SelectTrigger className="w-[120px]">
                <Calendar className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Period" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7days">7 Days</SelectItem>
                <SelectItem value="30days">30 Days</SelectItem>
                <SelectItem value="90days">90 Days</SelectItem>
                <SelectItem value="year">1 Year</SelectItem>
              </SelectContent>
            </Select>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleDataToggle}
            >
              {useRealData ? 'Use Mock Data' : 'Use Real Data'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={exportToCSV}
              disabled={isLoading || !data || data.length === 0}
            >
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="py-8 text-center">
            <p className="text-destructive mb-2">Error loading sales data</p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              Try Again
            </Button>
          </div>
        ) : (
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={data}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="sales"
                  stroke="#8884d8"
                  activeDot={{ r: 8 }}
                  name="Sales (€)"
                />
                <Line yAxisId="right" type="monotone" dataKey="orders" stroke="#82ca9d" name="Orders" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
