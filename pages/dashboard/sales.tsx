import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useWarehouses, useSalesData, useTopProducts, useSalesForecast } from '../../lib/hooks/useProHandelData';
import RevenueBreakdownChart from '../../components/charts/RevenueBreakdownChart';
import CategoryPerformanceChart from '../../components/charts/CategoryPerformanceChart';

// Sales Trend Chart Component
const SalesTrendChart = ({ warehouseId, period }) => {
  const { data: salesData, isLoading, error } = useSalesData(warehouseId, period);
  const { data: forecastData } = useSalesForecast(warehouseId, 14);

  if (isLoading) return <div className="loading">Loading sales trend data...</div>;
  if (error) return <div className="error">Error loading sales data: {error.message}</div>;
  
  // Get historical trend data
  const trendData = salesData?.trend || [];
  
  if (trendData.length === 0) {
    return <div className="no-data">No sales trend data available</div>;
  }
  
  // Format date for better display
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric'
    }).format(date);
  };
  
  // Calculate key metrics
  const currentTotal = trendData.reduce((sum, day) => sum + day.revenue, 0);
  const avgDaily = currentTotal / trendData.length;
  const maxDay = trendData.reduce((max, day) => Math.max(max, day.revenue), 0);
  const lastDay = trendData[trendData.length - 1]?.revenue || 0;
  
  // Calculate forecast (if available)
  const forecastTotal = forecastData?.reduce((sum, day) => sum + day.revenue, 0) || 0;
  const forecastGrowth = currentTotal > 0 ? ((forecastTotal - currentTotal) / currentTotal) * 100 : 0;
  
  return (
    <div className="sales-trend-chart">
      <h3>Sales Trend and Forecast</h3>
      
      <div className="metrics-grid" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '15px',
        margin: '20px 0'
      }}>
        <div className="metric-card" style={{
          padding: '15px',
          backgroundColor: '#f5f8ff',
          borderRadius: '8px',
          border: '1px solid #e0e6f5'
        }}>
          <div style={{ color: '#666', fontSize: '0.9em' }}>Total Revenue</div>
          <div style={{ fontSize: '1.4em', fontWeight: 'bold', marginTop: '5px' }}>
            ${currentTotal.toLocaleString()}
          </div>
        </div>
        
        <div className="metric-card" style={{
          padding: '15px',
          backgroundColor: '#f5f8ff',
          borderRadius: '8px',
          border: '1px solid #e0e6f5'
        }}>
          <div style={{ color: '#666', fontSize: '0.9em' }}>Avg. Daily</div>
          <div style={{ fontSize: '1.4em', fontWeight: 'bold', marginTop: '5px' }}>
            ${avgDaily.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </div>
        </div>
        
        <div className="metric-card" style={{
          padding: '15px',
          backgroundColor: '#f5f8ff',
          borderRadius: '8px',
          border: '1px solid #e0e6f5'
        }}>
          <div style={{ color: '#666', fontSize: '0.9em' }}>Best Day</div>
          <div style={{ fontSize: '1.4em', fontWeight: 'bold', marginTop: '5px' }}>
            ${maxDay.toLocaleString()}
          </div>
        </div>
        
        <div className="metric-card" style={{
          padding: '15px',
          backgroundColor: '#f5f8ff',
          borderRadius: '8px',
          border: '1px solid #e0e6f5'
        }}>
          <div style={{ color: '#666', fontSize: '0.9em' }}>Forecast Growth</div>
          <div style={{ 
            fontSize: '1.4em', 
            fontWeight: 'bold', 
            marginTop: '5px',
            color: forecastGrowth >= 0 ? '#2e7d32' : '#c62828'
          }}>
            {forecastGrowth >= 0 ? '+' : ''}{forecastGrowth.toFixed(1)}%
          </div>
        </div>
      </div>
      
      {/* We're reusing the CategoryPerformanceChart with showForecast true */}
      <CategoryPerformanceChart 
        warehouseId={warehouseId} 
        period={period}
        showForecast={true}
        height={350} 
      />
    </div>
  );
};

// Top Movers Component
const TopMoversComponent = ({ warehouseId, period }) => {
  const { data: topProducts, isLoading, error } = useTopProducts(warehouseId, 10);
  
  if (isLoading) return <div className="loading">Loading top products data...</div>;
  if (error) return <div className="error">Error loading products data: {error.message}</div>;
  
  if (!topProducts || topProducts.length === 0) {
    return <div className="no-data">No products data available</div>;
  }
  
  // Sort by growth (desc) and revenue (desc)
  const fastestGrowing = [...topProducts]
    .filter(p => p.growth > 0)
    .sort((a, b) => b.growth - a.growth)
    .slice(0, 5);
  
  const declining = [...topProducts]
    .filter(p => p.growth < 0)
    .sort((a, b) => a.growth - b.growth)
    .slice(0, 5);
  
  return (
    <div className="top-movers">
      <h3>Top Movers</h3>
      
      <div className="movers-grid" style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '20px',
        marginTop: '20px'
      }}>
        {/* Growing Products */}
        <div className="movers-section">
          <h4 style={{ 
            margin: '0 0 15px 0',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ color: '#2e7d32' }}>↑</span> Fastest Growing
          </h4>
          
          <div className="movers-list">
            {fastestGrowing.length > 0 ? (
              fastestGrowing.map((product, index) => (
                <div 
                  key={index}
                  className="mover-item"
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '12px',
                    backgroundColor: index % 2 === 0 ? '#f5f5f5' : 'white',
                    borderRadius: '4px',
                    marginBottom: '8px'
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 'bold' }}>{product.name || `Product ${product.productId}`}</div>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>
                      {product.categoryName || 'Uncategorized'}
                    </div>
                  </div>
                  <div style={{ 
                    textAlign: 'right',
                    paddingLeft: '15px',
                    borderLeft: '1px solid #eee'
                  }}>
                    <div>${product.revenue.toLocaleString()}</div>
                    <div style={{ 
                      color: '#2e7d32', 
                      fontWeight: 'bold' 
                    }}>
                      +{product.growth.toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-movers" style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                No growing products in this period
              </div>
            )}
          </div>
        </div>
        
        {/* Declining Products */}
        <div className="movers-section">
          <h4 style={{ 
            margin: '0 0 15px 0',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ color: '#c62828' }}>↓</span> Fastest Declining
          </h4>
          
          <div className="movers-list">
            {declining.length > 0 ? (
              declining.map((product, index) => (
                <div 
                  key={index}
                  className="mover-item"
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '12px',
                    backgroundColor: index % 2 === 0 ? '#f5f5f5' : 'white',
                    borderRadius: '4px',
                    marginBottom: '8px'
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 'bold' }}>{product.name || `Product ${product.productId}`}</div>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>
                      {product.categoryName || 'Uncategorized'}
                    </div>
                  </div>
                  <div style={{ 
                    textAlign: 'right',
                    paddingLeft: '15px',
                    borderLeft: '1px solid #eee'
                  }}>
                    <div>${product.revenue.toLocaleString()}</div>
                    <div style={{ 
                      color: '#c62828', 
                      fontWeight: 'bold' 
                    }}>
                      {product.growth.toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-movers" style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                No declining products in this period
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Sales Comparison Widget
const SalesComparisonWidget = ({ warehouses }) => {
  const [warehouse1, setWarehouse1] = useState<string | null>(null);
  const [warehouse2, setWarehouse2] = useState<string | null>(null);
  
  // Set default warehouses when data is available
  useEffect(() => {
    if (warehouses && warehouses.length >= 2 && !warehouse1 && !warehouse2) {
      setWarehouse1(warehouses[0].id);
      setWarehouse2(warehouses[1].id);
    }
  }, [warehouses, warehouse1, warehouse2]);
  
  return (
    <div className="sales-comparison-widget" style={{
      padding: '20px',
      backgroundColor: '#f5f8ff',
      borderRadius: '8px',
      border: '1px solid #e0e6f5'
    }}>
      <h3 style={{ margin: '0 0 15px 0' }}>Sales Comparison</h3>
      
      <div className="comparison-selectors" style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '20px'
      }}>
        <div style={{ flex: 1 }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>Warehouse 1:</label>
          <select
            value={warehouse1 || ''}
            onChange={(e) => setWarehouse1(e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ccc'
            }}
          >
            <option value="">Select Warehouse</option>
            {warehouses?.map(w => (
              <option key={w.id} value={w.id}>{w.name}</option>
            ))}
          </select>
        </div>
        
        <div style={{ marginTop: '25px', fontWeight: 'bold' }}>vs</div>
        
        <div style={{ flex: 1 }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>Warehouse 2:</label>
          <select
            value={warehouse2 || ''}
            onChange={(e) => setWarehouse2(e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ccc'
            }}
          >
            <option value="">Select Warehouse</option>
            {warehouses?.map(w => (
              <option key={w.id} value={w.id}>{w.name}</option>
            ))}
          </select>
        </div>
      </div>
      
      {warehouse1 && warehouse2 ? (
        <div className="comparison-chart" style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p>Comparison chart will be displayed here</p>
          {/* In a real implementation, you would use the useSalesComparison hook and display a chart */}
        </div>
      ) : (
        <div style={{ padding: '30px', textAlign: 'center', color: '#666' }}>
          Select two warehouses to compare their sales performance
        </div>
      )}
      
      <div style={{ marginTop: '15px', textAlign: 'right' }}>
        <button style={{
          padding: '8px 15px',
          backgroundColor: '#4a6ebb',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}>
          View Detailed Comparison
        </button>
      </div>
    </div>
  );
};

// Main Sales Page
const SalesPage: React.FC = () => {
  const router = useRouter();
  const [selectedWarehouse, setSelectedWarehouse] = useState<string | undefined>(undefined);
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d'>('30d');
  const { data: warehouses, isLoading: warehousesLoading } = useWarehouses();
  
  // Set the first warehouse as default when data loads
  useEffect(() => {
    if (warehouses && warehouses.length > 0 && !selectedWarehouse) {
      setSelectedWarehouse(warehouses[0].id);
    }
  }, [warehouses, selectedWarehouse]);
  
  return (
    <div className="sales-container" style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: 0 }}>Sales Dashboard</h1>
        
        <div className="controls" style={{ display: 'flex', gap: '15px' }}>
          {/* Warehouse selector */}
          <div className="warehouse-selector">
            <label htmlFor="warehouse" style={{ marginRight: '8px' }}>Warehouse:</label>
            <select
              id="warehouse"
              value={selectedWarehouse}
              onChange={(e) => setSelectedWarehouse(e.target.value)}
              disabled={warehousesLoading}
              style={{ 
                padding: '8px 12px',
                borderRadius: '4px',
                border: '1px solid #ccc'
              }}
            >
              {warehousesLoading ? (
                <option>Loading warehouses...</option>
              ) : warehouses?.length ? (
                warehouses.map(warehouse => (
                  <option key={warehouse.id} value={warehouse.id}>
                    {warehouse.name}
                  </option>
                ))
              ) : (
                <option>No warehouses available</option>
              )}
            </select>
          </div>
          
          {/* Period selector */}
          <div className="period-selector">
            <label htmlFor="period" style={{ marginRight: '8px' }}>Period:</label>
            <select
              id="period"
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value as '7d' | '30d' | '90d')}
              style={{ 
                padding: '8px 12px',
                borderRadius: '4px',
                border: '1px solid #ccc'
              }}
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
          </div>
          
          {/* Export button */}
          <button style={{ 
            padding: '8px 15px',
            backgroundColor: '#4a6ebb',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '5px'
          }}>
            <span>Export Data</span>
            <span>📊</span>
          </button>
        </div>
      </header>
      
      {/* Navigation tabs */}
      <div className="dashboard-nav" style={{ 
        display: 'flex',
        borderBottom: '1px solid #e0e0e0',
        marginBottom: '20px'
      }}>
        {['Overview', 'Sales', 'Inventory', 'AI Insights'].map(tab => (
          <div 
            key={tab}
            className={`nav-tab ${tab.toLowerCase() === 'sales' ? 'active' : ''}`}
            onClick={() => router.push(`/dashboard/${tab.toLowerCase().replace(' ', '-')}`)}
            style={{ 
              padding: '12px 20px',
              cursor: 'pointer',
              borderBottom: tab.toLowerCase() === 'sales' 
                ? '2px solid #4a6ebb' 
                : '2px solid transparent',
              color: tab.toLowerCase() === 'sales' ? '#4a6ebb' : '#666',
              fontWeight: tab.toLowerCase() === 'sales' ? 'bold' : 'normal'
            }}
          >
            {tab}
          </div>
        ))}
      </div>
      
      {/* Main sales content */}
      <div className="sales-content" style={{ 
        display: 'grid',
        gridTemplateColumns: '2fr 1fr',
        gap: '20px',
        marginBottom: '30px'
      }}>
        {/* Main column */}
        <div className="main-column">
          {/* Sales Trend Chart */}
          <div className="chart-container" style={{ 
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            marginBottom: '20px'
          }}>
            <SalesTrendChart warehouseId={selectedWarehouse} period={selectedPeriod} />
          </div>
          
          {/* Revenue Breakdown Chart */}
          <div className="chart-container" style={{ 
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <RevenueBreakdownChart 
              warehouseId={selectedWarehouse} 
              period={selectedPeriod}
            />
          </div>
        </div>
        
        {/* Side column */}
        <div className="side-column">
          {/* Top Movers */}
          <div className="side-section" style={{ 
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            marginBottom: '20px'
          }}>
            <TopMoversComponent
              warehouseId={selectedWarehouse}
              period={selectedPeriod}
            />
          </div>
          
          {/* Sales Comparison */}
          <div className="side-section">
            <SalesComparisonWidget warehouses={warehouses} />
          </div>
        </div>
      </div>
      
      {/* Additional insights section */}
      <div className="sales-insights" style={{ 
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '30px'
      }}>
        <h3>Sales Insights</h3>
        
        <div className="insights-grid" style={{ 
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '20px',
          marginTop: '20px'
        }}>
          {/* These would come from actual data in production */}
          <div className="insight-card" style={{ 
            padding: '15px',
            backgroundColor: '#f5f8ff',
            borderRadius: '8px',
            border: '1px solid #e0e6f5'
          }}>
            <h4 style={{ 
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              margin: '0 0 10px 0',
              color: '#4285F4'
            }}>
              <span>💡</span> Top Insight
            </h4>
            <p style={{ margin: '0 0 10px 0' }}>
              Your top 5 products account for 47% of total revenue. Consider featuring these products prominently.
            </p>
          </div>
          
          <div className="insight-card" style={{ 
            padding: '15px',
            backgroundColor: '#f5f8ff',
            borderRadius: '8px',
            border: '1px solid #e0e6f5'
          }}>
            <h4 style={{ 
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              margin: '0 0 10px 0',
              color: '#EA4335'
            }}>
              <span>⚠️</span> Attention Needed
            </h4>
            <p style={{ margin: '0 0 10px 0' }}>
              Sales in the "Electronics" category have declined by 15% compared to the previous period.
            </p>
          </div>
          
          <div className="insight-card" style={{ 
            padding: '15px',
            backgroundColor: '#f5f8ff',
            borderRadius: '8px',
            border: '1px solid #e0e6f5'
          }}>
            <h4 style={{ 
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              margin: '0 0 10px 0',
              color: '#34A853'
            }}>
              <span>📈</span> Growth Opportunity
            </h4>
            <p style={{ margin: '0 0 10px 0' }}>
              Weekend sales are 35% higher than weekday sales. Consider running weekday promotions to boost revenue.
            </p>
          </div>
        </div>
      </div>
      
      {/* Call to action section */}
      <div className="cta-section" style={{ 
        backgroundColor: '#4a6ebb',
        color: 'white',
        borderRadius: '8px',
        padding: '25px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h3 style={{ margin: '0 0 10px 0' }}>Need Deeper Sales Analysis?</h3>
          <p style={{ margin: 0, maxWidth: '600px' }}>
            Get AI-powered insights with our ProHandel Assistant to uncover hidden patterns and sales opportunities.
          </p>
        </div>
        
        <button 
          onClick={() => router.push('/dashboard/ai-insights')}
          style={{ 
            padding: '10px 20px',
            backgroundColor: 'white',
            color: '#4a6ebb',
            border: 'none',
            borderRadius: '4px',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
        >
          Open AI Insights
        </button>
      </div>
    </div>
  );
};

export default SalesPage;
