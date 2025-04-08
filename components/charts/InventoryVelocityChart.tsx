import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';
import { useInventoryData, useSalesData } from '../../lib/hooks/useProHandelData';

interface InventoryVelocityChartProps {
  warehouseId?: string;
  period?: '7d' | '30d' | '90d';
  categoryLimit?: number;
  height?: number;
}

const InventoryVelocityChart: React.FC<InventoryVelocityChartProps> = ({
  warehouseId,
  period = '30d',
  categoryLimit = 10,
  height = 400
}) => {
  // Fetch inventory and sales data using our hooks
  const { data: inventoryData, isLoading: inventoryLoading, error: inventoryError } = useInventoryData(warehouseId);
  const { data: salesData, isLoading: salesLoading, error: salesError } = useSalesData(warehouseId, period);
  
  // Calculate inventory velocity (ratio of sales to inventory)
  const chartData = useMemo(() => {
    if (!inventoryData || !salesData || !inventoryData.byCategory || !salesData.byCategory) {
      return [];
    }
    
    // Map inventory categories with sales data
    const velocityData = inventoryData.byCategory.map(inventoryCat => {
      // Find matching sales category
      const salesCat = salesData.byCategory.find(s => s.categoryId === inventoryCat.categoryId) || {
        revenue: 0,
        orderCount: 0,
        percentOfTotal: 0,
        growth: 0
      };
      
      // Calculate velocity metrics
      const inventoryValue = inventoryCat.inventoryValue || 0;
      const salesValue = salesCat.revenue || 0;
      
      // Avoid division by zero
      const turnoverRatio = inventoryValue > 0 ? salesValue / inventoryValue : 0;
      const velocity = turnoverRatio * 100; // Scale for visualization
      
      // Calculate days of inventory (based on current sales rate)
      // Higher is worse (more days of inventory sitting around)
      const daysOfInventory = salesValue > 0 
        ? (inventoryValue / salesValue) * (period === '7d' ? 7 : period === '30d' ? 30 : 90)
        : inventoryCat.productCount > 0 ? 999 : 0; // If products but no sales, assign 999 days
      
      return {
        name: inventoryCat.name,
        categoryId: inventoryCat.categoryId,
        velocity,
        turnoverRatio,
        daysOfInventory,
        inventoryValue,
        salesValue,
        productCount: inventoryCat.productCount,
        lowStockCount: inventoryCat.lowStockCount,
        outOfStockCount: inventoryCat.outOfStockCount,
        // Risk score: higher is worse (combines slow velocity with stockouts)
        riskScore: (inventoryCat.lowStockCount / Math.max(inventoryCat.productCount, 1)) * 100
      };
    });
    
    // Sort by velocity (descending) and limit to top categories
    return velocityData
      .sort((a, b) => b.velocity - a.velocity)
      .slice(0, categoryLimit);
  }, [inventoryData, salesData, period, categoryLimit]);
  
  // Custom tooltip for the bar chart
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="inventory-tooltip" style={{
          backgroundColor: '#fff',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p className="tooltip-category" style={{ fontWeight: 'bold', margin: 0 }}>{data.name}</p>
          <p className="tooltip-turnover" style={{ margin: '5px 0' }}>
            Turnover Ratio: {data.turnoverRatio.toFixed(2)}x
          </p>
          <p className="tooltip-days" style={{ 
            margin: '5px 0',
            color: data.daysOfInventory > 60 ? 'red' : data.daysOfInventory > 30 ? 'orange' : 'green'
          }}>
            Days of Inventory: {data.daysOfInventory > 900 ? '999+' : data.daysOfInventory.toFixed(0)}
          </p>
          <p className="tooltip-value" style={{ margin: '5px 0' }}>
            Inventory Value: ${data.inventoryValue.toLocaleString()}
          </p>
          <p className="tooltip-sales" style={{ margin: '5px 0' }}>
            Sales Value: ${data.salesValue.toLocaleString()}
          </p>
          <div className="tooltip-stock-status" style={{ marginTop: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Products:</span>
              <span>{data.productCount}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Low Stock:</span>
              <span style={{ color: 'orange' }}>{data.lowStockCount}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Out of Stock:</span>
              <span style={{ color: 'red' }}>{data.outOfStockCount}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };
  
  // Handle loading and error states
  const isLoading = inventoryLoading || salesLoading;
  const error = inventoryError || salesError;
  
  if (isLoading) {
    return <div className="chart-loading">Loading inventory velocity data...</div>;
  }
  
  if (error) {
    return <div className="chart-error">Error loading inventory data: {error.message}</div>;
  }
  
  if (!chartData.length) {
    return <div className="chart-empty">No inventory velocity data available</div>;
  }
  
  // Calculate chart metrics
  const averageVelocity = chartData.reduce((sum, item) => sum + item.velocity, 0) / chartData.length;
  const optimalVelocity = Math.max(...chartData.map(item => item.velocity)) * 0.8; // 80% of max as "optimal"
  
  return (
    <div className="inventory-velocity-chart">
      <h3>Inventory Velocity by Category</h3>
      <div className="chart-period">{period === '7d' ? 'Last 7 Days' : period === '30d' ? 'Last 30 Days' : 'Last 90 Days'}</div>
      
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="name" 
            angle={-45} 
            textAnchor="end" 
            height={70}
            interval={0}
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            label={{ value: 'Inventory Velocity', angle: -90, position: 'insideLeft' }}
            tickFormatter={(value) => `${value.toFixed(0)}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <ReferenceLine y={averageVelocity} stroke="#888" strokeDasharray="3 3">
            <Label value="Average" position="insideBottomRight" />
          </ReferenceLine>
          <ReferenceLine y={optimalVelocity} stroke="#00C49F" strokeDasharray="3 3">
            <Label value="Optimal" position="insideTopRight" />
          </ReferenceLine>
          <Bar 
            dataKey="velocity" 
            name="Inventory Velocity" 
            fill="#8884d8"
            radius={[4, 4, 0, 0]}
          />
          <Bar 
            dataKey="riskScore" 
            name="Risk Score" 
            fill="#FF8042"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
      
      <div className="chart-insights">
        <div className="insight-card" style={{ backgroundColor: '#f0f4f8', padding: '10px', borderRadius: '4px', marginTop: '10px' }}>
          <h4 style={{ margin: '0 0 8px 0' }}>Inventory Insights</h4>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            <li>
              {chartData.length > 0 ? `${chartData[0].name} has the highest turnover rate` : 'No turnover data available'}
            </li>
            <li>
              {chartData.filter(c => c.daysOfInventory > 60).length > 0 
                ? `${chartData.filter(c => c.daysOfInventory > 60).length} categories have over 60 days of inventory`
                : 'All categories have healthy inventory levels'}
            </li>
            <li>
              {chartData.filter(c => c.outOfStockCount > 0).length > 0
                ? `${chartData.filter(c => c.outOfStockCount > 0).reduce((sum, c) => sum + c.outOfStockCount, 0)} products are out of stock`
                : 'No products are currently out of stock'}
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default InventoryVelocityChart;
