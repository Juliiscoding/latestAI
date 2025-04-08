import React, { useState, useEffect, useRef } from 'react';
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
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

const AIInsightsPanel: React.FC<AIInsightsPanelProps> = ({
  warehouseId,
  userId,
  initialPrompt = "Give me a summary of the current performance"
}) => {
  // Fetch AI context data using our hook
  const { data: aiContext, isLoading, error } = useAIAssistantContext(warehouseId);
  
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
    if (!messageText.trim() || !threadId || !aiContext) return;
    
    try {
      setIsThinking(true);
      
      // Add user message to UI
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: messageText,
        timestamp: new Date()
      };
      
      if (!isInitial) {
        setMessages(prev => [...prev, userMessage]);
        setInput('');
      }
      
      // Send message to assistant
      const { runId } = await sendMessageToAssistant(
        threadId,
        messageText,
        aiContext
      );
      
      // Poll for response
      const pollInterval = setInterval(async () => {
        try {
          const result = await checkRunStatus(
            threadId, 
            runId,
            handleToolCall
          );
          
          if (result.status === 'completed') {
            clearInterval(pollInterval);
            
            // Get the latest assistant message
            const assistantMessage = result.messages
              .filter(msg => msg.role === 'assistant')
              .pop();
            
            if (assistantMessage) {
              // Add assistant message to UI
              const newMessage: Message = {
                id: `assistant-${Date.now()}`,
                role: 'assistant',
                content: assistantMessage.content,
                timestamp: new Date()
              };
              
              setMessages(prev => [...prev, newMessage]);
            }
            
            setIsThinking(false);
          } else if (['failed', 'cancelled', 'expired'].includes(result.status)) {
            clearInterval(pollInterval);
            setIsThinking(false);
            
            // Add error message
            const errorMessage: Message = {
              id: `error-${Date.now()}`,
              role: 'system',
              content: `Sorry, I encountered an error. Please try again.`,
              timestamp: new Date()
            };
            
            setMessages(prev => [...prev, errorMessage]);
          }
        } catch (error) {
          clearInterval(pollInterval);
          setIsThinking(false);
          console.error('Error polling for assistant response:', error);
        }
      }, 1000);
      
    } catch (error) {
      setIsThinking(false);
      console.error('Error sending message to assistant:', error);
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
      <div className="ai-insights-loading" style={{ padding: '20px', textAlign: 'center' }}>
        <div className="loading-spinner" style={{ marginBottom: '10px' }}></div>
        <p>Loading AI Insights...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="ai-insights-error" style={{ padding: '20px', color: '#e53935' }}>
        <h3>Error Loading AI Insights</h3>
        <p>{error.message}</p>
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
};

export default AIInsightsPanel;
