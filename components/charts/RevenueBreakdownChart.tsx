import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend
} from 'recharts';
import { useSalesData } from '../../lib/hooks/useProHandelData';

interface RevenueBreakdownChartProps {
  warehouseId?: string;
  period?: '7d' | '30d' | '90d';
  height?: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#8dd1e1', '#a4de6c', '#d0ed57'];

const RevenueBreakdownChart: React.FC<RevenueBreakdownChartProps> = ({
  warehouseId,
  period = '30d',
  height = 300
}) => {
  // Fetch sales data using our hook
  const { data: salesData, isLoading, error } = useSalesData(warehouseId, period);
  
  // Process data for the chart
  const chartData = useMemo(() => {
    if (!salesData?.byCategory?.length) return [];
    
    // Sort categories by revenue (descending)
    const sortedCategories = [...salesData.byCategory].sort((a, b) => b.revenue - a.revenue);
    
    // Take top 9 categories and group the rest as "Other"
    const TOP_CATEGORIES_COUNT = 9;
    
    if (sortedCategories.length <= TOP_CATEGORIES_COUNT) {
      return sortedCategories.map(category => ({
        name: category.name,
        value: category.revenue,
        growth: category.growth
      }));
    }
    
    // Get top categories
    const topCategories = sortedCategories.slice(0, TOP_CATEGORIES_COUNT);
    
    // Calculate "Other" category
    const otherCategories = sortedCategories.slice(TOP_CATEGORIES_COUNT);
    const otherRevenue = otherCategories.reduce((sum, cat) => sum + cat.revenue, 0);
    const weightedGrowth = otherCategories.reduce(
      (sum, cat) => sum + (cat.growth * cat.revenue), 
      0
    ) / otherRevenue;
    
    return [
      ...topCategories.map(category => ({
        name: category.name,
        value: category.revenue,
        growth: category.growth
      })),
      {
        name: 'Other',
        value: otherRevenue,
        growth: weightedGrowth
      }
    ];
  }, [salesData]);
  
  // Custom tooltip for the chart
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip" style={{ 
          backgroundColor: '#fff',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p className="tooltip-label" style={{ fontWeight: 'bold', margin: 0 }}>{data.name}</p>
          <p className="tooltip-revenue" style={{ margin: '5px 0' }}>
            Revenue: ${data.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className="tooltip-percent" style={{ margin: 0 }}>
            {(data.value / salesData.totalRevenue * 100).toFixed(1)}% of total
          </p>
          <p className="tooltip-growth" style={{ 
            margin: '5px 0 0 0',
            color: data.growth >= 0 ? 'green' : 'red' 
          }}>
            Growth: {data.growth > 0 ? '+' : ''}{data.growth.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };
  
  // Handle loading and error states
  if (isLoading) {
    return <div className="chart-loading">Loading revenue breakdown...</div>;
  }
  
  if (error) {
    return <div className="chart-error">Error loading revenue data: {error.message}</div>;
  }
  
  if (!chartData.length) {
    return <div className="chart-empty">No revenue data available for this period</div>;
  }
  
  return (
    <div className="revenue-breakdown-chart">
      <h3>Revenue Breakdown by Product Line</h3>
      <div className="chart-period">{period === '7d' ? 'Last 7 Days' : period === '30d' ? 'Last 30 Days' : 'Last 90 Days'}</div>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            innerRadius={40}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <div className="chart-totals">
        <div className="total-revenue">
          <span className="label">Total Revenue:</span>
          <span className="value">${salesData?.totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        </div>
        <div className="total-orders">
          <span className="label">Total Orders:</span>
          <span className="value">{salesData?.totalOrders.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};

export default RevenueBreakdownChart;
