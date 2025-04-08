import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import { useWarehouses, useAIAssistantContext } from '../../lib/hooks/useProHandelData';
import AIInsightsPanel from '../../components/ai/AIInsightsPanel';

// Define types for the card components
interface CardProps {
  title: string;
  icon: React.ReactNode;
  description: string;
  onSelect: () => void;
  isSelected: boolean;
}

// Analysis Category Component
const AnalysisCategory: React.FC<CardProps> = ({ title, icon, description, onSelect, isSelected }) => {
  return (
    <div 
      className={`analysis-category ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
      style={{
        padding: '15px',
        borderRadius: '8px',
        border: `1px solid ${isSelected ? '#4a6ebb' : '#e0e0e0'}`,
        backgroundColor: isSelected ? '#f0f4ff' : 'white',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        marginBottom: '12px'
      }}
    >
      <div className="category-header" style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        marginBottom: '5px'
      }}>
        <div className="category-icon" style={{
          fontSize: '1.6em',
          width: '40px',
          height: '40px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: isSelected ? '#4a6ebb25' : '#f5f5f5',
          borderRadius: '8px'
        }}>
          {icon}
        </div>
        <h3 style={{ margin: 0, color: isSelected ? '#4a6ebb' : 'initial' }}>{title}</h3>
      </div>
      <p style={{ 
        margin: '0',
        fontSize: '0.9em',
        color: '#666'
      }}>
        {description}
      </p>
    </div>
  );
};

// Type for insights message
interface InsightsMessage {
  title: string;
  content: string;
  type: 'opportunity' | 'risk' | 'insight' | 'other';
  date: string;
}

// Insight Card Component
const InsightCard: React.FC<InsightsMessage> = ({ title, content, type, date }) => {
  // Determine styling based on insight type
  const getTypeStyle = (type: string) => {
    switch (type) {
      case 'opportunity':
        return { 
          color: '#34A853', 
          icon: '📈', 
          bgColor: '#e8f5e9',
          borderColor: '#c8e6c9'
        };
      case 'risk':
        return { 
          color: '#EA4335', 
          icon: '⚠️', 
          bgColor: '#ffebee',
          borderColor: '#ffcdd2'
        };
      case 'insight':
      default:
        return { 
          color: '#4285F4', 
          icon: '💡', 
          bgColor: '#e3f2fd',
          borderColor: '#bbdefb'
        };
    }
  };
  
  const typeStyle = getTypeStyle(type);
  
  return (
    <div className="insight-card" style={{
      padding: '15px',
      backgroundColor: typeStyle.bgColor,
      border: `1px solid ${typeStyle.borderColor}`,
      borderRadius: '8px',
      marginBottom: '15px'
    }}>
      <div className="insight-header" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '10px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{ fontSize: '1.2em' }}>{typeStyle.icon}</span>
          <h4 style={{ margin: 0, color: typeStyle.color }}>{title}</h4>
        </div>
        <span style={{ fontSize: '0.8em', color: '#666' }}>{date}</span>
      </div>
      
      <div className="insight-content" style={{ fontSize: '0.95em' }}>
        {content}
      </div>
    </div>
  );
};

// AI Insights Page
const AIInsightsPage: React.FC = () => {
  const router = useRouter();
  const [selectedWarehouse, setSelectedWarehouse] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('overview');
  const [question, setQuestion] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [aiResponse, setAiResponse] = useState<string>('');
  const { data: warehouseData, isLoading: warehousesLoading } = useWarehouses();
  const { data: aiContext, isLoading: contextLoading } = useAIAssistantContext(selectedWarehouse, { enabled: !!selectedWarehouse });
  const inputRef = useRef<HTMLInputElement>(null);
  const aiPanelRef = useRef<any>(null);
  
  // Set the first warehouse as default when data loads
  useEffect(() => {
    if (warehouseData && warehouseData.length > 0 && !selectedWarehouse) {
      setSelectedWarehouse(warehouseData[0].id);
    }
  }, [warehouseData, selectedWarehouse]);
  
  // Analysis categories
  const analysisCategories = [
    {
      id: 'overview',
      title: 'Business Overview',
      icon: '📊',
      description: 'Overall business health, top metrics and trends'
    },
    {
      id: 'inventory',
      title: 'Inventory Optimization',
      icon: '📦',
      description: 'Stock levels, reordering suggestions, and stockout risk assessment'
    },
    {
      id: 'sales',
      title: 'Sales Analysis',
      icon: '💰',
      description: 'Revenue patterns, top performers, and growth opportunities'
    },
    {
      id: 'forecasting',
      title: 'Demand Forecasting',
      icon: '🔮',
      description: 'Predictive analysis for inventory planning and sales'
    },
    {
      id: 'competitive',
      title: 'Competitive Analysis',
      icon: '🏆',
      description: 'Compare performance across warehouses and markets'
    }
  ];
  
  // Sample pre-generated insights (these would come from the AI in production)
  const sampleInsights: InsightsMessage[] = [
    {
      title: 'Revenue Acceleration Opportunity',
      content: 'Based on sales patterns, bundling "Premium Drill Set" with "Safety Goggles" could increase average order value by 12%. Customers who purchase drills often buy safety equipment separately within 7 days.',
      type: 'opportunity',
      date: 'Today'
    },
    {
      title: 'Inventory Risk Alert',
      content: 'Five high-selling products are projected to stockout within 14 days based on current demand. Consider expediting the restock process to avoid approximately $15,000 in lost sales.',
      type: 'risk',
      date: 'Yesterday'
    },
    {
      title: 'Seasonal Trend Identified',
      content: 'Sales of outdoor equipment increase by 35% during April-June. Consider increasing inventory levels and marketing spend for these categories starting in March to capitalize on seasonal demand.',
      type: 'insight',
      date: '3 days ago'
    },
    {
      title: 'Cross-Selling Opportunity',
      content: 'Customers who purchase "Power Washers" rarely buy "Cleaning Solution" in the same transaction, but data shows they typically return to purchase it within 2 weeks. Add cleaning solution recommendations to power washer product pages.',
      type: 'opportunity',
      date: '1 week ago'
    }
  ];
  
  // Sample recommended questions
  const recommendedQuestions = [
    "What are my top selling products this month?",
    "Which categories have the highest profit margin?",
    "What products are at risk of stockout in the next 14 days?",
    "Where are my sales opportunities for next quarter?",
    "How is my inventory turnover rate compared to industry average?",
    "Which products should I consider discontinuing?"
  ];
  
  // Function to send question to AI assistant
  const handleSendQuestion = async () => {
    if (!question.trim() || !selectedWarehouse) return;
    
    try {
      setLoading(true);
      
      // Call our AI API endpoint
      const response = await fetch('/api/ai/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: question.trim(),
          warehouseId: selectedWarehouse,
          userId: `user-${Date.now()}`
        })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error: ${response.status} ${errorText}`);
      }
      
      const data = await response.json();
      setAiResponse(data.answer || 'Sorry, I could not generate a response.');
      
      // Clear input after sending
      setQuestion('');
      if (inputRef.current) {
        inputRef.current.value = '';
      }
      
      // Update the panel component
      if (aiPanelRef.current && typeof aiPanelRef.current.handleSendMessage === 'function') {
        aiPanelRef.current.handleSendMessage(question.trim());
      }
      
    } catch (error) {
      console.error('Error sending question to AI:', error);
      alert(`Error: ${error instanceof Error ? error.message : 'Failed to process your request'}`);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="ai-insights-container" style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: 0 }}>AI Insights</h1>
        
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
              ) : warehouseData?.length ? (
                warehouseData.map(warehouse => (
                  <option key={warehouse.id} value={warehouse.id}>
                    {warehouse.name}
                  </option>
                ))
              ) : (
                <option>No warehouses available</option>
              )}
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
            className={`nav-tab ${tab.toLowerCase() === 'ai insights' || tab.toLowerCase() === 'ai-insights' ? 'active' : ''}`}
            onClick={() => router.push(`/dashboard/${tab.toLowerCase().replace(' ', '-')}`)}
            style={{ 
              padding: '12px 20px',
              cursor: 'pointer',
              borderBottom: tab.toLowerCase() === 'ai insights' || tab.toLowerCase() === 'ai-insights'
                ? '2px solid #4a6ebb' 
                : '2px solid transparent',
              color: tab.toLowerCase() === 'ai insights' || tab.toLowerCase() === 'ai-insights' ? '#4a6ebb' : '#666',
              fontWeight: tab.toLowerCase() === 'ai insights' || tab.toLowerCase() === 'ai-insights' ? 'bold' : 'normal'
            }}
          >
            {tab}
          </div>
        ))}
      </div>
      
      {/* Main content grid */}
      <div className="ai-insights-grid" style={{
        display: 'grid',
        gridTemplateColumns: '320px 1fr',
        gap: '25px'
      }}>
        {/* Left sidebar for categories */}
        <div className="ai-categories">
          <h2 style={{ marginTop: 0, marginBottom: '20px' }}>Analysis Categories</h2>
          
          {analysisCategories.map(category => (
            <AnalysisCategory
              key={category.id}
              title={category.title}
              icon={category.icon}
              description={category.description}
              isSelected={selectedCategory === category.id}
              onSelect={() => setSelectedCategory(category.id)}
            />
          ))}
        </div>
        
        {/* Main content area */}
        <div className="ai-content">
          {/* AI Assistant Panel */}
          <div className="assistant-section" style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            marginBottom: '25px'
          }}>
            <h2 style={{ marginTop: 0, marginBottom: '20px' }}>ProHandel Assistant</h2>
            
            <div className="ai-insights-panel">
              <AIInsightsPanel 
                warehouseId={selectedWarehouse}
                userId={`user-${Date.now()}`}
                contextData={aiContext}
                isLoading={contextLoading}
              />
            </div>
            
            <div className="ai-query-input" style={{ 
              marginTop: '20px', 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <input 
                type="text" 
                placeholder="Ask a question about your data..." 
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendQuestion();
                  }
                }}
                style={{ 
                  flex: 1,
                  padding: '12px 16px',
                  borderRadius: '4px',
                  border: '1px solid #ccc',
                  fontSize: '1em'
                }}
                ref={inputRef}
              />
              <button 
                onClick={handleSendQuestion}
                disabled={loading || contextLoading || !selectedWarehouse}
                style={{
                  padding: '12px 20px',
                  backgroundColor: loading || contextLoading || !selectedWarehouse ? '#a0a0a0' : '#4a6ebb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  marginLeft: '10px',
                  cursor: loading || contextLoading || !selectedWarehouse ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                {loading ? (
                  <span className="loading-spinner" style={{ 
                    width: '20px', 
                    height: '20px',
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderTop: '2px solid white',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }}></span>
                ) : 'Ask AI'}
              </button>
            </div>
            
            <div className="recommended-questions" style={{
              marginTop: '15px'
            }}>
              <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '8px' }}>
                Try asking:
              </div>
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '8px'
              }}>
                {recommendedQuestions.map((q, i) => (
                  <div
                    key={i}
                    onClick={() => setQuestion(q)}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: '#f0f4ff',
                      borderRadius: '20px',
                      fontSize: '0.9em',
                      cursor: 'pointer',
                      border: '1px solid #d0d9f0'
                    }}
                  >
                    {q}
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          {/* Recent Insights */}
          <div className="insights-section" style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '20px'
            }}>
              <h2 style={{ margin: 0 }}>Recent Insights</h2>
              <button style={{
                padding: '8px 15px',
                backgroundColor: 'transparent',
                border: '1px solid #ccc',
                borderRadius: '4px',
                cursor: 'pointer'
              }}>
                View All Insights
              </button>
            </div>
            
            <div className="insights-list">
              {sampleInsights.map((insight, index) => (
                <InsightCard
                  key={index}
                  title={insight.title}
                  content={insight.content}
                  type={insight.type}
                  date={insight.date}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIInsightsPage;
