import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useWarehouses, useInventoryData, useStockoutRisks } from '../../lib/hooks/useProHandelData';
import InventoryVelocityChart from '../../components/charts/InventoryVelocityChart';

// Inventory Risk Matrix Component
const InventoryRiskMatrix = ({ warehouseId }) => {
  const { data: stockoutRisks, isLoading, error } = useStockoutRisks(warehouseId);
  
  if (isLoading) return <div className="loading">Loading inventory risk data...</div>;
  if (error) return <div className="error">Error loading risk data: {error.message}</div>;
  if (!stockoutRisks || stockoutRisks.length === 0) {
    return <div className="no-data">No inventory risk data available</div>;
  }
  
  // Group products by risk level
  const riskGroups = {
    critical: stockoutRisks.filter(item => item.riskLevel === 'critical'),
    high: stockoutRisks.filter(item => item.riskLevel === 'high'),
    medium: stockoutRisks.filter(item => item.riskLevel === 'medium'),
    low: stockoutRisks.filter(item => item.riskLevel === 'low')
  };
  
  return (
    <div className="inventory-risk-matrix">
      <h3>Inventory Risk Matrix</h3>
      
      <div className="risk-grid" style={{ 
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '15px',
        marginTop: '15px'
      }}>
        {Object.entries(riskGroups).map(([level, items]) => (
          <div 
            key={level}
            className={`risk-section risk-${level}`}
            style={{ 
              backgroundColor: 
                level === 'critical' ? '#ffebee' : 
                level === 'high' ? '#fff8e1' : 
                level === 'medium' ? '#e8f5e9' : 
                '#e3f2fd',
              borderRadius: '8px',
              padding: '15px',
              border: `1px solid ${
                level === 'critical' ? '#ffcdd2' : 
                level === 'high' ? '#ffe0b2' : 
                level === 'medium' ? '#c8e6c9' : 
                '#bbdefb'
              }`
            }}
          >
            <h4 style={{ 
              margin: '0 0 10px 0',
              color: 
                level === 'critical' ? '#c62828' : 
                level === 'high' ? '#ef6c00' : 
                level === 'medium' ? '#2e7d32' : 
                '#1565c0',
              textTransform: 'capitalize'
            }}>
              {level} Risk
              <span style={{ 
                marginLeft: '8px',
                fontSize: '0.9em', 
                fontWeight: 'normal',
                backgroundColor: 'rgba(255,255,255,0.7)',
                padding: '2px 6px',
                borderRadius: '12px'
              }}>
                {items.length} items
              </span>
            </h4>
            
            {items.length > 0 ? (
              <div className="risk-items" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                {items.map((item, index) => (
                  <div 
                    key={index}
                    className="risk-item"
                    style={{ 
                      padding: '8px 10px',
                      backgroundColor: 'rgba(255,255,255,0.7)',
                      marginBottom: '8px',
                      borderRadius: '4px',
                      fontSize: '0.9em'
                    }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '3px' }}>{item.name}</div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      fontSize: '0.85em',
                      color: '#555'
                    }}>
                      <span>Stock: {item.stockLevel}</span>
                      <span>Reorder: {item.reorderPoint}</span>
                      {item.daysUntilStockout !== undefined && (
                        <span style={{ 
                          fontWeight: 'bold',
                          color: item.daysUntilStockout < 7 ? '#c62828' : '#555'
                        }}>
                          {item.daysUntilStockout} days left
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-items" style={{ padding: '15px', textAlign: 'center', color: '#666' }}>
                No items at this risk level
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Category Drilldown Component
const CategoryDrilldown = ({ warehouseId }) => {
  const { data: inventoryData, isLoading, error } = useInventoryData(warehouseId);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  
  if (isLoading) return <div className="loading">Loading category data...</div>;
  if (error) return <div className="error">Error loading category data: {error.message}</div>;
  if (!inventoryData?.byCategory || inventoryData.byCategory.length === 0) {
    return <div className="no-data">No category data available</div>;
  }
  
  // Sort categories by inventory value
  const sortedCategories = [...inventoryData.byCategory].sort(
    (a, b) => b.inventoryValue - a.inventoryValue
  );
  
  // Get details for the selected category
  const selectedCategoryData = selectedCategory 
    ? sortedCategories.find(cat => cat.categoryId === selectedCategory)
    : null;
  
  return (
    <div className="category-drilldown">
      <h3>Inventory by Category</h3>
      
      <div className="category-grid" style={{ 
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
        gap: '10px',
        marginTop: '15px',
        marginBottom: '20px'
      }}>
        {sortedCategories.map(category => (
          <div 
            key={category.categoryId}
            className={`category-card ${category.categoryId === selectedCategory ? 'selected' : ''}`}
            onClick={() => setSelectedCategory(
              category.categoryId === selectedCategory ? null : category.categoryId
            )}
            style={{ 
              padding: '12px',
              borderRadius: '6px',
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: category.categoryId === selectedCategory ? '#e3f2fd' : 'white',
              border: `1px solid ${category.categoryId === selectedCategory ? '#2196f3' : '#ddd'}`,
              transition: 'all 0.2s ease'
            }}
          >
            <div className="category-name" style={{ 
              fontWeight: 'bold',
              marginBottom: '6px',
              fontSize: '0.9em',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }}>
              {category.name}
            </div>
            <div className="product-count" style={{ fontSize: '0.8em', color: '#666' }}>
              {category.productCount} products
            </div>
            <div className="inventory-value" style={{ 
              marginTop: '5px',
              fontWeight: category.categoryId === selectedCategory ? 'bold' : 'normal'
            }}>
              ${category.inventoryValue.toLocaleString()}
            </div>
          </div>
        ))}
      </div>
      
      {selectedCategoryData && (
        <div className="category-details" style={{ 
          backgroundColor: '#f8f9fa',
          padding: '15px',
          borderRadius: '8px',
          marginTop: '10px'
        }}>
          <h4>{selectedCategoryData.name} Details</h4>
          <div className="details-grid" style={{ 
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '15px',
            marginTop: '10px'
          }}>
            <div className="detail-card" style={{ 
              padding: '10px',
              backgroundColor: 'white',
              borderRadius: '6px',
              textAlign: 'center'
            }}>
              <div className="detail-label" style={{ color: '#666', fontSize: '0.8em' }}>Products</div>
              <div className="detail-value" style={{ fontSize: '1.4em', fontWeight: 'bold' }}>
                {selectedCategoryData.productCount}
              </div>
            </div>
            <div className="detail-card" style={{ 
              padding: '10px',
              backgroundColor: 'white',
              borderRadius: '6px',
              textAlign: 'center'
            }}>
              <div className="detail-label" style={{ color: '#666', fontSize: '0.8em' }}>Total Value</div>
              <div className="detail-value" style={{ fontSize: '1.4em', fontWeight: 'bold' }}>
                ${selectedCategoryData.inventoryValue.toLocaleString()}
              </div>
            </div>
            <div className="detail-card" style={{ 
              padding: '10px',
              backgroundColor: 'white',
              borderRadius: '6px',
              textAlign: 'center'
            }}>
              <div className="detail-label" style={{ color: '#666', fontSize: '0.8em' }}>Low Stock</div>
              <div className="detail-value" style={{ 
                fontSize: '1.4em', 
                fontWeight: 'bold',
                color: selectedCategoryData.lowStockCount > 0 ? '#ef6c00' : 'inherit'
              }}>
                {selectedCategoryData.lowStockCount}
              </div>
            </div>
            <div className="detail-card" style={{ 
              padding: '10px',
              backgroundColor: 'white',
              borderRadius: '6px',
              textAlign: 'center'
            }}>
              <div className="detail-label" style={{ color: '#666', fontSize: '0.8em' }}>Out of Stock</div>
              <div className="detail-value" style={{ 
                fontSize: '1.4em', 
                fontWeight: 'bold',
                color: selectedCategoryData.outOfStockCount > 0 ? '#c62828' : 'inherit'
              }}>
                {selectedCategoryData.outOfStockCount}
              </div>
            </div>
          </div>
          
          <div className="category-actions" style={{ 
            marginTop: '15px',
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '10px'
          }}>
            <button style={{ 
              padding: '6px 12px',
              backgroundColor: 'transparent',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer'
            }}>
              Export Data
            </button>
            <button style={{ 
              padding: '6px 12px',
              backgroundColor: '#4a6ebb',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}>
              View Products
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Main Inventory Page
const InventoryPage: React.FC = () => {
  const router = useRouter();
  const [selectedWarehouse, setSelectedWarehouse] = useState<string | undefined>(undefined);
  const { data: warehouses, isLoading: warehousesLoading } = useWarehouses();
  
  // Set the first warehouse as default when data loads
  useEffect(() => {
    if (warehouses && warehouses.length > 0 && !selectedWarehouse) {
      setSelectedWarehouse(warehouses[0].id);
    }
  }, [warehouses, selectedWarehouse]);
  
  // Inventory KPIs - these would come from your data hooks in production
  const inventoryKPIs = [
    {
      label: 'Total Products',
      value: '1,254',
      icon: '📦',
      color: '#4285F4'
    },
    {
      label: 'Inventory Value',
      value: '$825,430',
      icon: '💰',
      color: '#34A853'
    },
    {
      label: 'Out of Stock',
      value: '28',
      icon: '⚠️',
      color: '#EA4335'
    },
    {
      label: 'Low Stock',
      value: '57',
      icon: '📉',
      color: '#FBBC05'
    }
  ];
  
  return (
    <div className="inventory-container" style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: 0 }}>Inventory Management</h1>
        
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
            <span>Export Inventory</span>
            <span>📋</span>
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
            className={`nav-tab ${tab.toLowerCase() === 'inventory' ? 'active' : ''}`}
            onClick={() => router.push(`/dashboard/${tab.toLowerCase().replace(' ', '-')}`)}
            style={{ 
              padding: '12px 20px',
              cursor: 'pointer',
              borderBottom: tab.toLowerCase() === 'inventory' 
                ? '2px solid #4a6ebb' 
                : '2px solid transparent',
              color: tab.toLowerCase() === 'inventory' ? '#4a6ebb' : '#666',
              fontWeight: tab.toLowerCase() === 'inventory' ? 'bold' : 'normal'
            }}
          >
            {tab}
          </div>
        ))}
      </div>
      
      {/* Inventory KPIs */}
      <div className="inventory-kpis" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '15px',
        marginBottom: '25px'
      }}>
        {inventoryKPIs.map((kpi, index) => (
          <div 
            key={index}
            className="kpi-card"
            style={{
              backgroundColor: 'white',
              padding: '15px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <div>
              <div style={{ color: '#666', fontSize: '0.9em', marginBottom: '5px' }}>{kpi.label}</div>
              <div style={{ fontSize: '1.5em', fontWeight: 'bold' }}>{kpi.value}</div>
            </div>
            <div style={{
              width: '40px',
              height: '40px',
              backgroundColor: `${kpi.color}15`,
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5em'
            }}>
              {kpi.icon}
            </div>
          </div>
        ))}
      </div>
      
      {/* Main content grid */}
      <div className="inventory-grid" style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '20px',
        marginBottom: '25px'
      }}>
        {/* Risk Matrix */}
        <div className="inventory-section" style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <InventoryRiskMatrix warehouseId={selectedWarehouse} />
        </div>
        
        {/* Category Drilldown */}
        <div className="inventory-section" style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <CategoryDrilldown warehouseId={selectedWarehouse} />
        </div>
      </div>
      
      {/* Inventory Velocity Chart */}
      <div className="inventory-section" style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '25px'
      }}>
        <InventoryVelocityChart warehouseId={selectedWarehouse} categoryLimit={10} height={400} />
      </div>
      
      {/* Quick Actions */}
      <div className="inventory-actions" style={{ marginTop: '25px' }}>
        <h3>Quick Actions</h3>
        <div style={{ 
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: '15px',
          marginTop: '10px'
        }}>
          {[
            { name: 'Reorder Low Stock', icon: '🔁' },
            { name: 'Print Inventory Report', icon: '🖨️' },
            { name: 'Sync with POS', icon: '🔄' },
            { name: 'AI Inventory Analysis', icon: '🤖' }
          ].map((action, index) => (
            <div
              key={index}
              className="action-card"
              style={{
                padding: '15px',
                backgroundColor: 'white',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                transition: 'all 0.2s'
              }}
            >
              <span style={{ fontSize: '1.5em' }}>{action.icon}</span>
              <span>{action.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default InventoryPage;
