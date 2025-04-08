import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useWarehouses } from '../../lib/hooks/useProHandelData';
import RevenueBreakdownChart from '../../components/charts/RevenueBreakdownChart';
import CategoryPerformanceChart from '../../components/charts/CategoryPerformanceChart';
import AIInsightsPanel from '../../components/ai/AIInsightsPanel';
import SalesDropWidget from '../../components/widgets/SalesDropWidget';

// KPI Card component
interface KPICardProps {
  title: string;
  value: string;
  trend: 'up' | 'down' | 'neutral';
  trendValue: string;
  icon: React.ReactNode;
  color: string;
}

const KPICard: React.FC<KPICardProps> = ({ title, value, trend, trendValue, icon, color }) => (
  <div className="kpi-card" style={{ 
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column'
  }}>
    <div className="card-header" style={{ 
      display: 'flex', 
      justifyContent: 'space-between',
      marginBottom: '10px'
    }}>
      <h3 style={{ margin: 0, color: '#333', fontSize: '16px' }}>{title}</h3>
      <div className="card-icon" style={{ 
        width: '36px',
        height: '36px',
        backgroundColor: `${color}20`,
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: color
      }}>
        {icon}
      </div>
    </div>
    
    <div className="card-value" style={{ 
      fontSize: '24px',
      fontWeight: 'bold',
      margin: '5px 0'
    }}>
      {value}
    </div>
    
    <div className="card-trend" style={{ 
      display: 'flex',
      alignItems: 'center',
      color: trend === 'up' ? '#4caf50' : trend === 'down' ? '#f44336' : '#757575',
      fontSize: '14px'
    }}>
      {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
      {trendValue}
      <span style={{ marginLeft: '5px', color: '#757575' }}>vs previous period</span>
    </div>
  </div>
);

const DashboardOverview: React.FC = () => {
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
  
  // Mock KPI data - in production this would come from real data hooks
  const kpiData = [
    {
      title: 'Total Revenue',
      value: '$124,568',
      trend: 'up' as const,
      trendValue: '8.2%',
      icon: '💰',
      color: '#4285F4'
    },
    {
      title: 'Total Orders',
      value: '1,254',
      trend: 'up' as const,
      trendValue: '5.1%',
      icon: '📦',
      color: '#34A853'
    },
    {
      title: 'Avg Order Value',
      value: '$99.34',
      trend: 'up' as const,
      trendValue: '3.0%',
      icon: '📊',
      color: '#FBBC05'
    },
    {
      title: 'Inventory Health',
      value: '92%',
      trend: 'down' as const,
      trendValue: '2.3%',
      icon: '📈',
      color: '#EA4335'
    }
  ];
  
  // Generate a stable user ID for the AI assistant
  const userId = 'user-1234'; // In production this would be the actual user ID
  
  return (
    <div className="dashboard-container" style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: 0 }}>ProHandel Dashboard</h1>
        
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
            className={`nav-tab ${tab.toLowerCase() === 'overview' ? 'active' : ''}`}
            onClick={() => router.push(`/dashboard/${tab.toLowerCase().replace(' ', '-')}`)}
            style={{ 
              padding: '12px 20px',
              cursor: 'pointer',
              borderBottom: tab.toLowerCase() === 'overview' 
                ? '2px solid #4a6ebb' 
                : '2px solid transparent',
              color: tab.toLowerCase() === 'overview' ? '#4a6ebb' : '#666',
              fontWeight: tab.toLowerCase() === 'overview' ? 'bold' : 'normal'
            }}
          >
            {tab}
          </div>
        ))}
      </div>
      
      {/* KPI Cards */}
      <div className="kpi-cards" style={{ 
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
        gap: '20px',
        marginBottom: '30px'
      }}>
        {kpiData.map((kpi, index) => (
          <KPICard key={index} {...kpi} />
        ))}
      </div>
      
      {/* Main content - 2 column layout */}
      <div className="dashboard-content" style={{ 
        display: 'grid',
        gridTemplateColumns: '2fr 1fr',
        gap: '20px',
        marginBottom: '30px'
      }}>
        {/* Charts column */}
        <div className="charts-column">
          {/* Category Performance chart */}
          <div className="chart-container" style={{ 
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            marginBottom: '20px'
          }}>
            <CategoryPerformanceChart 
              warehouseId={selectedWarehouse} 
              period={selectedPeriod}
              showForecast={true}
            />
          </div>
          
          {/* Sales Drop Analysis Widget */}
          <div className="chart-container" style={{ 
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            marginBottom: '20px',
            overflow: 'hidden'
          }}>
            <SalesDropWidget
              warehouseId={selectedWarehouse}
              tenant={process.env.TENANT_ID || 'default'}
              onRefresh={() => console.log('Widget refreshed')}
            />
          </div>
          
          {/* Revenue Breakdown chart */}
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
        
        {/* AI Insights column */}
        <div className="ai-column">
          <div className="ai-container" style={{ 
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            height: '100%',
            overflow: 'hidden'
          }}>
            <AIInsightsPanel 
              warehouseId={selectedWarehouse}
              userId={userId}
              initialPrompt="Give me a summary of the current business performance and highlight any areas that need attention."
            />
          </div>
        </div>
      </div>
      
      {/* Quick links to other dashboard pages */}
      <div className="dashboard-quick-links" style={{ marginTop: '20px' }}>
        <h3>Quick Actions</h3>
        <div className="quick-links-grid" style={{ 
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: '15px',
          marginTop: '10px'
        }}>
          {[
            { name: 'View Sales Details', path: '/dashboard/sales', icon: '📊' },
            { name: 'Check Inventory', path: '/dashboard/inventory', icon: '📦' },
            { name: 'Ask AI Assistant', path: '/dashboard/ai-insights', icon: '🤖' },
            { name: 'Export Reports', path: '#', icon: '📑' }
          ].map((link, index) => (
            <div 
              key={index}
              className="quick-link-card"
              onClick={() => router.push(link.path)}
              style={{ 
                padding: '15px',
                borderRadius: '8px',
                backgroundColor: '#f5f8ff',
                border: '1px solid #e0e6f5',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                transition: 'all 0.2s ease'
              }}
            >
              <span style={{ fontSize: '24px' }}>{link.icon}</span>
              <span>{link.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;
