import React, { useMemo, useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';
import { useSalesData, useSalesForecast } from '../../lib/hooks/useProHandelData';

interface CategoryPerformanceChartProps {
  warehouseId?: string;
  period?: '7d' | '30d' | '90d';
  showForecast?: boolean;
  height?: number;
}

const CategoryPerformanceChart: React.FC<CategoryPerformanceChartProps> = ({
  warehouseId,
  period = '30d',
  showForecast = true,
  height = 400
}) => {
  // Store the selected category (if user clicks on one)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  
  // Fetch sales data using our hook
  const { data: salesData, isLoading, error } = useSalesData(warehouseId, period);
  
  // Fetch forecast data if showForecast is enabled
  const { 
    data: forecastData, 
    isLoading: forecastLoading, 
    error: forecastError 
  } = useSalesForecast(warehouseId, 14, { enabled: showForecast });
  
  // Process data for the chart
  const chartData = useMemo(() => {
    if (!salesData?.trend) return [];
    
    // Get the trend data from sales (daily/weekly data points)
    const trendData = [...salesData.trend];
    
    // Add forecast data if available
    if (showForecast && forecastData?.length) {
      // Append forecast data to the trend
      trendData.push(...forecastData.map(point => ({
        ...point,
        isForecast: true
      })));
    }
    
    return trendData;
  }, [salesData, forecastData, showForecast]);
  
  // Get category data for the selected category or all categories
  const categoryData = useMemo(() => {
    if (!salesData?.byCategory) return [];
    
    // If specific category is selected, filter to just that one
    if (selectedCategory) {
      return salesData.byCategory.filter(cat => cat.categoryId === selectedCategory);
    }
    
    // Otherwise return top 5 categories by revenue
    return [...salesData.byCategory]
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 5);
  }, [salesData, selectedCategory]);
  
  // Custom tooltip for the chart
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const isForecast = payload[0].payload.isForecast;
      
      return (
        <div className="category-tooltip" style={{
          backgroundColor: '#fff',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p className="tooltip-date" style={{ fontWeight: 'bold', margin: 0 }}>
            {label} {isForecast ? '(Forecast)' : ''}
          </p>
          <p className="tooltip-revenue" style={{ margin: '5px 0' }}>
            Revenue: ${payload[0].value.toLocaleString()}
          </p>
          {payload[1] && (
            <p className="tooltip-orders" style={{ margin: '5px 0' }}>
              Orders: {payload[1].value}
            </p>
          )}
          {isForecast && (
            <p className="tooltip-forecast" style={{ fontStyle: 'italic', margin: '5px 0', color: '#888' }}>
              Forecast based on historical data
            </p>
          )}
        </div>
      );
    }
    return null;
  };
  
  // Handle loading and error states
  if (isLoading || (showForecast && forecastLoading)) {
    return <div className="chart-loading">Loading performance data...</div>;
  }
  
  if (error || (showForecast && forecastError)) {
    return <div className="chart-error">Error loading performance data: {(error || forecastError)?.message}</div>;
  }
  
  if (!chartData.length) {
    return <div className="chart-empty">No performance data available for this period</div>;
  }
  
  // Format date for better display
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(date);
  };
  
  // Calculate target/forecast threshold (e.g., 5% above last period's average)
  const pastDataPoints = chartData.filter(point => !point.isForecast);
  const pastAverage = pastDataPoints.reduce((sum, item) => sum + item.revenue, 0) / pastDataPoints.length;
  const targetThreshold = pastAverage * 1.05; // 5% growth target
  
  return (
    <div className="category-performance-chart">
      <h3>Category Performance {showForecast ? 'vs Forecast' : ''}</h3>
      <div className="chart-period">{period === '7d' ? 'Last 7 Days' : period === '30d' ? 'Last 30 Days' : 'Last 90 Days'}</div>
      
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 70 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            angle={-45} 
            textAnchor="end" 
            height={70}
            interval="preserveStartEnd"
            tickFormatter={formatDate}
          />
          <YAxis 
            yAxisId="left"
            label={{ value: 'Revenue ($)', angle: -90, position: 'insideLeft' }}
            tickFormatter={(value) => `$${value.toLocaleString()}`}
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            label={{ value: 'Orders', angle: 90, position: 'insideRight' }}
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ bottom: 0 }} />
          
          {/* Target/Forecast threshold line */}
          <ReferenceLine 
            y={targetThreshold} 
            yAxisId="left" 
            stroke="#FF8042" 
            strokeDasharray="3 3" 
            label={{ value: 'Target', position: 'insideBottomRight' }}
          />
          
          {/* Actual revenue line */}
          <Line
            type="monotone"
            dataKey="revenue"
            name="Revenue"
            stroke="#8884d8"
            yAxisId="left"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
          
          {/* Forecast line (dashed) */}
          {showForecast && (
            <Line
              type="monotone"
              dataKey={(item) => item.isForecast ? item.revenue : null}
              name="Forecast"
              stroke="#8884d8"
              strokeDasharray="5 5"
              yAxisId="left"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          )}
          
          {/* Orders bar */}
          <Bar 
            dataKey="orders" 
            name="Orders" 
            fill="#82ca9d"
            yAxisId="right"
            radius={[4, 4, 0, 0]}
          />
        </ComposedChart>
      </ResponsiveContainer>
      
      {/* Category breakdown section */}
      <div className="category-breakdown" style={{ marginTop: '20px' }}>
        <h4>Top Performing Categories</h4>
        <div className="category-grid" style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', 
          gap: '10px',
          marginTop: '10px'
        }}>
          {categoryData.map(category => (
            <div 
              key={category.categoryId}
              className="category-card" 
              onClick={() => setSelectedCategory(
                category.categoryId === selectedCategory ? null : category.categoryId
              )}
              style={{
                padding: '10px',
                borderRadius: '6px',
                backgroundColor: category.categoryId === selectedCategory ? '#e3f2fd' : '#f5f5f5',
                cursor: 'pointer',
                border: category.categoryId === selectedCategory ? '1px solid #2196f3' : '1px solid #ddd'
              }}
            >
              <div className="category-name" style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                {category.name}
              </div>
              <div className="category-revenue" style={{ marginBottom: '3px' }}>
                ${category.revenue.toLocaleString()}
              </div>
              <div className="category-growth" style={{ 
                color: category.growth >= 0 ? 'green' : 'red',
                fontWeight: category.growth >= 10 || category.growth <= -10 ? 'bold' : 'normal'
              }}>
                {category.growth > 0 ? '↑' : '↓'} {Math.abs(category.growth).toFixed(1)}%
              </div>
              <div className="category-percent" style={{ fontSize: '0.9em', color: '#666', marginTop: '3px' }}>
                {category.percentOfTotal.toFixed(1)}% of total
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Performance insights */}
      <div className="performance-insights" style={{ marginTop: '20px' }}>
        <div className="insight-card" style={{ backgroundColor: '#f0f4f8', padding: '15px', borderRadius: '6px' }}>
          <h4 style={{ margin: '0 0 10px 0' }}>Performance Insights</h4>
          {categoryData.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              <li>
                {categoryData[0].name} is your top performing category ({categoryData[0].percentOfTotal.toFixed(1)}% of revenue)
              </li>
              {categoryData.find(c => c.growth > 10) && (
                <li>
                  {categoryData.find(c => c.growth > 10)?.name} is growing rapidly ({categoryData.find(c => c.growth > 10)?.growth.toFixed(1)}%)
                </li>
              )}
              {categoryData.find(c => c.growth < -10) && (
                <li>
                  {categoryData.find(c => c.growth < -10)?.name} is declining ({categoryData.find(c => c.growth < -10)?.growth.toFixed(1)}%)
                </li>
              )}
              {showForecast && (
                <li>
                  Revenue forecast predicts {
                    forecastData && forecastData.length > 0 && salesData && salesData.totalRevenue
                      ? forecastData.reduce((sum, day) => sum + day.revenue, 0) > salesData.totalRevenue
                        ? 'growth'
                        : 'decline'
                      : 'stable performance'
                  } in the next 14 days
                </li>
              )}
            </ul>
          ) : (
            <p>No category data available for this period.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default CategoryPerformanceChart;
