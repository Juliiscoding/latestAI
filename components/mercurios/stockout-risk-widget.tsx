'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Loader2, Download } from 'lucide-react';
import prohandelClient from '@/lib/mercurios/clients/prohandel-client';
import { useStockoutRisk } from '@/lib/hooks/use-prohandel-data';

interface StockoutRiskWidgetProps {
  warehouseId?: string | null;
}

interface StockoutRiskItem {
  id: string;
  name: string;
  category: string;
  currentStock: number;
  reorderPoint: number;
  risk: number;
  estimatedDaysToStockout: number;
}

export default function StockoutRiskWidget({ warehouseId = null }: StockoutRiskWidgetProps) {
  const [useRealData, setUseRealData] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);

  // Use our custom hook for data fetching
  const { data, isLoading, error, refetch } = useStockoutRisk({ 
    useRealData, 
    warehouseId 
  });

  const stockoutItems = data?.data || [];

  const testConnection = async () => {
    setTestingConnection(true);
    try {
      console.log('Testing ProHandel connection...');
      const result = await prohandelClient.testProHandelConnection();
      console.log('Connection test result:', result);
      alert('ProHandel connection successful! Check console for details.');
    } catch (error) {
      console.error('Connection test failed:', error);
      alert('ProHandel connection failed. Check console for details.');
    } finally {
      setTestingConnection(false);
    }
  };

  const handleDataToggle = () => {
    setUseRealData(!useRealData);
  };

  const getRiskBadge = (risk: number) => {
    if (risk >= 80) return <Badge variant="destructive">Critical</Badge>;
    if (risk >= 50) return <Badge variant="secondary">High</Badge>;
    if (risk >= 20) return <Badge variant="outline">Medium</Badge>;
    return <Badge variant="secondary">Low</Badge>;
  };

  // Function to export data as CSV
  const exportToCSV = () => {
    if (!stockoutItems || stockoutItems.length === 0) return;
    
    // Create CSV content
    const headers = ['ID', 'Name', 'Category', 'Current Stock', 'Reorder Point', 'Risk (%)', 'Days to Stockout'];
    const csvContent = [
      headers.join(','),
      ...stockoutItems.map((item: StockoutRiskItem) => 
        `${item.id},"${item.name}","${item.category}",${item.currentStock},${item.reorderPoint},${item.risk},${item.estimatedDaysToStockout}`
      )
    ].join('\n');
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `stockout-risk-${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Stockout Risk</CardTitle>
          <CardDescription>Products that may run out of stock soon</CardDescription>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted-foreground">Use Real Data</span>
            <Switch checked={useRealData} onCheckedChange={handleDataToggle} />
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={exportToCSV}
            disabled={isLoading || !stockoutItems || stockoutItems.length === 0}
          >
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex justify-end mb-4">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={testConnection}
            disabled={testingConnection}
          >
            {testingConnection ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Testing...
              </>
            ) : (
              'Test ProHandel Connection'
            )}
          </Button>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="py-8 text-center">
            <p className="text-destructive mb-2">Error loading data</p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              Try Again
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {stockoutItems.length === 0 ? (
              <p className="text-center py-8 text-muted-foreground">No stockout risks detected</p>
            ) : (
              stockoutItems.map((item: StockoutRiskItem) => (
                <div key={item.id} className="border rounded-md p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-medium">{item.name}</h3>
                      <p className="text-sm text-muted-foreground">{item.category}</p>
                    </div>
                    {getRiskBadge(item.risk)}
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Current Stock: {item.currentStock}</span>
                      <span>Reorder Point: {item.reorderPoint}</span>
                    </div>
                    <Progress value={item.risk} className="h-2" />
                    <p className="text-xs text-muted-foreground">
                      {item.estimatedDaysToStockout <= 0
                        ? 'Out of stock'
                        : `Est. days to stockout: ${item.estimatedDaysToStockout}`}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
