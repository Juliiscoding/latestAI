import React, { useState, useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import { useAIAssistantContext } from '../../lib/hooks/useProHandelData';
import { 
  getOrCreateThread, 
  sendMessageToAssistant, 
  checkRunStatus, 
  generateSystemInstructions
} from '../../lib/ai/prohandelAssistant';

interface AIInsightsPanelProps {
  warehouseId?: string;
  userId: string;
  initialPrompt?: string;
  contextData?: any;
  isLoading?: boolean;
  categoryFilter?: string;
  error?: Error | string | null;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  sources?: any[];
  isError?: boolean;
}

// Export the panel methods for ref access
export interface AIInsightsPanelHandle {
  handleSendMessage: (message: string) => void;
}

const AIInsightsPanel = forwardRef<AIInsightsPanelHandle, AIInsightsPanelProps>(({
  warehouseId,
  userId,
  initialPrompt = "Give me a summary of the current performance",
  contextData,
  isLoading: externalLoading,
  categoryFilter,
  error
}, ref) => {
  // Local state
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [autoQuestions, setAutoQuestions] = useState<string[]>([
    "Why did my sales drop last week?",
    "What products are at risk of stockout?",
    "Which category is growing the fastest?",
    "Recommend inventory optimization strategies"
  ]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Use passed context data if available, otherwise fetch it
  const { 
    data: fetchedContext, 
    isLoading: fetchLoading,
    error: fetchError
  } = useAIAssistantContext(warehouseId, { enabled: !contextData });
  
  const aiContext = contextData || fetchedContext;
  const isLoading = externalLoading || fetchLoading;
  
  // Expose methods to parent via ref
  useImperativeHandle(ref, () => ({
    handleSendMessage: (message: string) => {
      handleSendMessage(message, false);
    }
  }));
  
  // Initialize thread and load initial prompt
  useEffect(() => {
    const initializeAssistant = async () => {
      try {
        if (!userId) return;
        
        // Get or create a thread for the user
        const thread = await getOrCreateThread(userId);
        setThreadId(thread.id);
        
        // If there are no messages yet, send the initial prompt
        if (messages.length === 0 && aiContext) {
          handleSendMessage(initialPrompt, true);
        }
      } catch (error) {
        console.error('Error initializing assistant:', error);
      }
    };
    
    if (aiContext && !isLoading) {
      initializeAssistant();
    }
  }, [aiContext, userId, isLoading, initialPrompt, messages.length]);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  // Handle sending a message to the assistant
  const handleSendMessage = async (messageText: string, isInitial = false) => {
    if (!messageText.trim()) return;
    
    try {
      // Add user message to the chat
      const userMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'user',
        content: messageText,
        timestamp: new Date()
      };
      
      setMessages(prevMessages => [...prevMessages, userMessage]);
      setInput('');
      
      // Show loading state
      setIsThinking(true);
      
      // Call the AI API endpoint - now using direct MCP API URL
      const mcpApiUrl = process.env.NEXT_PUBLIC_MCP_API_URL || 'https://mcp.mercurios.ai/api';
      const response = await fetch(`${mcpApiUrl}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'tenant-id': userId.split('-')[0] || 'mercurios'
        },
        body: JSON.stringify({
          tool: 'ask-assistant',
          params: {
            prompt: messageText,
            context: {
              warehouseId,
              userId,
              categoryFilter
            },
            threadId: threadId
          }
        })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error: ${response.status} ${errorText}`);
      }
      
      const data = await response.json();
      
      // Add AI response to the chat
      const aiMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: data.answer || 'Sorry, I could not generate a response at this time.',
        timestamp: new Date(),
        sources: data.sources || []
      };
      
      setMessages(prevMessages => [...prevMessages, aiMessage]);
      setIsThinking(false);
      
      // Scroll to the bottom of the chat
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
      }
      
    } catch (error: unknown) {
      console.error('Error sending message to AI:', error);
      setIsThinking(false);
      
      // Add error message to the chat
      const errorMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'system',
        content: `An error occurred: ${formatError(error)}. Please try again.`,
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    }
  };
  
  // Handle tool calls from the assistant
  const handleToolCall = async (toolCall: any) => {
    try {
      const { id, name, arguments: args } = toolCall;
      
      // Implement handlers for each function
      switch (name) {
        case 'get_warehouse_details':
          // Mock implementation - would fetch real data in production
          return JSON.stringify({
            id: args.warehouse_id,
            name: `Warehouse ${args.warehouse_id}`,
            productCount: 1250,
            totalValue: 850000,
            address: "123 Warehouse Ln, Business District",
            manager: "Jane Smith"
          });
          
        case 'get_product_details':
          // Mock implementation
          return JSON.stringify({
            id: args.product_id,
            name: "Product XYZ",
            category: "Electronics",
            price: 299.99,
            stockLevel: 42,
            reorderPoint: 15,
            leadTime: "3-5 days",
            supplier: "Acme Supplies, Inc."
          });
          
        case 'get_category_performance':
          // Mock implementation
          return JSON.stringify({
            categoryId: args.category_id,
            name: "Category XYZ",
            period: args.period || "30d",
            revenue: 125000,
            growth: 12.5,
            productCount: 37,
            topProduct: "Product ABC",
            marketShare: "23.5%"
          });
          
        case 'generate_inventory_recommendations':
          // Mock implementation
          return JSON.stringify({
            warehouseId: args.warehouse_id,
            recommendations: [
              "Increase stock of fast-moving products in Category A",
              "Reduce inventory of seasonal items with low sales",
              "Implement cross-docking for high-volume items",
              "Set up automatic reordering for critical products"
            ],
            potentialSavings: "$15,000 per month",
            implementationTimeframe: "2-4 weeks"
          });
          
        default:
          return JSON.stringify({ error: `Unknown function: ${name}` });
      }
    } catch (error) {
      console.error('Error handling tool call:', error);
      return JSON.stringify({ error: `Failed to execute tool: ${error.message}` });
    }
  };
  
  // Format errors properly
  const formatError = (error: unknown): string => {
    if (error instanceof Error) {
      return error.message;
    } else if (typeof error === 'string') {
      return error;
    } else if (error && typeof error === 'object') {
      return JSON.stringify(error);
    }
    return 'Unknown error occurred';
  };

  const handleError = () => {
    // Combine errors from props and from the data hook
    const combinedError = error || fetchError;
    
    if (combinedError) {
      return (
        <div className="error-message" style={{ 
          padding: '10px 15px',
          backgroundColor: '#ffebee',
          color: '#c62828',
          borderRadius: '8px',
          margin: '10px 0'
        }}>
          <strong>Error:</strong> {formatError(combinedError)}
        </div>
      );
    }
    return null;
  };
  
  const formatTimestamp = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }).format(date);
  };
  
  // Handle loading and error states
  if (isLoading) {
    return (
      <div className="ai-insights-loading" style={{ 
        padding: '40px', 
        textAlign: 'center',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px'
      }}>
        <div className="loading-spinner" style={{ 
          margin: '0 auto 20px',
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #4a6ebb',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <p>Loading AI insights...</p>
      </div>
    );
  }
  
  // Handle potential error states
  if (!aiContext) {
    return (
      <div className="ai-insights-error" style={{ padding: '20px', color: '#e53935' }}>
        <h3>Error Loading AI Insights</h3>
        <p>Unable to load context data. Please try again later.</p>
        <button 
          onClick={() => window.location.reload()}
          style={{ padding: '8px 16px', marginTop: '10px' }}
        >
          Retry
        </button>
      </div>
    );
  }
  
  return (
    <div className="ai-insights-panel" style={{ 
      display: 'flex', 
      flexDirection: 'column',
      height: '100%',
      maxHeight: '600px',
      borderRadius: '8px',
      overflow: 'hidden',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
    }}>
      {/* Header */}
      <div className="insights-header" style={{ 
        padding: '15px 20px',
        backgroundColor: '#4a6ebb',
        color: 'white',
        fontWeight: 'bold',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h3 style={{ margin: 0 }}>ProHandel AI Insights</h3>
        <div className="assistant-status" style={{ 
          fontSize: '0.8rem',
          padding: '4px 8px',
          backgroundColor: isThinking ? '#ffa726' : '#66bb6a',
          borderRadius: '12px'
        }}>
          {isThinking ? 'Thinking...' : 'Ready'}
        </div>
      </div>
      
      {/* Messages container */}
      <div className="messages-container" style={{ 
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
        backgroundColor: '#f5f5f5'
      }}>
        {handleError()}
        {messages.length === 0 ? (
          <div className="welcome-message" style={{ 
            textAlign: 'center',
            padding: '40px 20px',
            color: '#666'
          }}>
            <h4>Welcome to ProHandel AI Insights</h4>
            <p>Ask me anything about your business data and I'll provide personalized insights.</p>
            <div className="suggested-questions" style={{ marginTop: '20px' }}>
              {autoQuestions.map((question, index) => (
                <button 
                  key={index}
                  onClick={() => handleSendMessage(question)}
                  style={{ 
                    display: 'block',
                    width: '100%',
                    textAlign: 'left',
                    padding: '10px 15px',
                    margin: '8px 0',
                    backgroundColor: 'white',
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map(message => (
            <div 
              key={message.id}
              className={`message ${message.role}`}
              style={{ 
                maxWidth: '80%',
                marginBottom: '10px',
                marginLeft: message.role === 'user' ? 'auto' : '0',
                marginRight: message.role === 'assistant' ? 'auto' : '0',
                padding: '10px 15px',
                borderRadius: '12px',
                backgroundColor: 
                  message.role === 'user' ? '#e3f2fd' : 
                  message.role === 'assistant' ? 'white' : 
                  '#ffebee',
                boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
              }}
            >
              <div className="message-content" style={{ marginBottom: '5px' }}>
                {message.content}
              </div>
              <div className="message-timestamp" style={{ 
                fontSize: '0.7rem', 
                textAlign: 'right',
                color: '#888'
              }}>
                {formatTimestamp(message.timestamp)}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input area */}
      <div className="input-container" style={{ 
        padding: '15px',
        backgroundColor: 'white',
        borderTop: '1px solid #e0e0e0',
        display: 'flex'
      }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(input)}
          placeholder="Ask something about your business data..."
          disabled={isThinking}
          style={{ 
            flex: 1,
            padding: '10px 15px',
            border: '1px solid #ddd',
            borderRadius: '20px',
            marginRight: '10px',
            fontSize: '14px',
            backgroundColor: isThinking ? '#f5f5f5' : 'white'
          }}
        />
        <button 
          onClick={() => handleSendMessage(input)}
          disabled={isThinking || !input.trim()}
          style={{ 
            padding: '8px 16px',
            backgroundColor: '#4a6ebb',
            color: 'white',
            border: 'none',
            borderRadius: '20px',
            cursor: isThinking ? 'not-allowed' : 'pointer',
            opacity: isThinking || !input.trim() ? 0.7 : 1
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
});

export default AIInsightsPanel;
