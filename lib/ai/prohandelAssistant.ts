/**
 * ProHandel AI Assistant Integration
 * 
 * This module integrates with OpenAI Assistants API to provide intelligent
 * analysis and insights based on ProHandel data.
 */
import OpenAI from 'openai';
import { Thread } from 'openai/resources/beta/threads/threads';
import { RunSubmitToolOutputsParams } from 'openai/resources/beta/threads/runs/runs';
import { AIDataContext } from '../data/prohandel';

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || '',
  dangerouslyAllowBrowser: true // Only for client-side usage
});

// Assistant ID for ProHandel insights (this would be created in your OpenAI account)
const ASSISTANT_ID = process.env.OPENAI_ASSISTANT_ID || '';

// Interface for function calls from the assistant
interface FunctionCall {
  name: string;
  arguments: string;
}

// Interface for assistant message
interface AssistantMessage {
  role: 'assistant' | 'user' | 'system';
  content: string;
  function_call?: FunctionCall;
}

/**
 * Initialize or retrieve an existing thread for the user
 * @param userId Unique identifier for the user
 * @returns Thread object from OpenAI
 */
export async function getOrCreateThread(userId: string): Promise<Thread> {
  try {
    // Store the thread ID in localStorage
    const threadIdKey = `prohandel_thread_${userId}`;
    const existingThreadId = localStorage.getItem(threadIdKey);
    
    if (existingThreadId) {
      try {
        // Try to retrieve the existing thread
        const thread = await openai.beta.threads.retrieve(existingThreadId);
        return thread;
      } catch (error) {
        console.warn('Could not retrieve existing thread, creating a new one:', error);
        // If retrieving fails (thread might have been deleted), create a new one
        localStorage.removeItem(threadIdKey);
      }
    }
    
    // Create a new thread if none exists
    const thread = await openai.beta.threads.create();
    localStorage.setItem(threadIdKey, thread.id);
    return thread;
  } catch (error) {
    console.error('Error in getOrCreateThread:', error);
    throw new Error('Failed to create or retrieve thread');
  }
}

/**
 * Send a message to the ProHandel assistant
 * @param threadId Thread ID
 * @param message User's message
 * @param contextData Current ProHandel data context
 * @returns Assistant's response
 */
export async function sendMessageToAssistant(
  threadId: string,
  message: string,
  contextData: AIDataContext
): Promise<{ messageId: string; runId: string }> {
  try {
    // First, add the context message to provide data to the assistant
    await openai.beta.threads.messages.create(threadId, {
      role: 'user',
      content: `[CONTEXT DATA - DO NOT RESPOND TO THIS MESSAGE DIRECTLY]\n${JSON.stringify(contextData)}`
    });
    
    // Add the user's actual message
    const userMessage = await openai.beta.threads.messages.create(threadId, {
      role: 'user',
      content: message
    });
    
    // Run the assistant
    const run = await openai.beta.threads.runs.create(threadId, {
      assistant_id: ASSISTANT_ID
    });
    
    return { messageId: userMessage.id, runId: run.id };
  } catch (error) {
    console.error('Error sending message to assistant:', error);
    throw new Error('Failed to send message to assistant');
  }
}

/**
 * Check the status of a run and handle tool calls
 * @param threadId Thread ID
 * @param runId Run ID
 * @param onToolCall Callback to handle tool calls
 * @returns Run status data
 */
export async function checkRunStatus(
  threadId: string,
  runId: string,
  onToolCall?: (toolCall: any) => Promise<string>
): Promise<{ status: string; messages: AssistantMessage[] }> {
  try {
    const run = await openai.beta.threads.runs.retrieve(threadId, runId);
    
    // Handle required actions (tool calls)
    if (run.status === 'requires_action' && run.required_action?.type === 'submit_tool_outputs') {
      const toolCalls = run.required_action.submit_tool_outputs.tool_calls;
      const toolOutputs: RunSubmitToolOutputsParams.ToolOutput[] = [];
      
      // Process each tool call
      if (onToolCall) {
        for (const toolCall of toolCalls) {
          const functionName = toolCall.function.name;
          const functionArgs = JSON.parse(toolCall.function.arguments);
          
          try {
            // Call the handler to execute the tool
            const result = await onToolCall({
              id: toolCall.id,
              name: functionName,
              arguments: functionArgs
            });
            
            toolOutputs.push({
              tool_call_id: toolCall.id,
              output: result
            });
          } catch (error) {
            console.error(`Error executing tool ${functionName}:`, error);
            toolOutputs.push({
              tool_call_id: toolCall.id,
              output: JSON.stringify({ error: `Failed to execute ${functionName}: ${error.message}` })
            });
          }
        }
      }
      
      // Submit the tool outputs back to the assistant
      await openai.beta.threads.runs.submitToolOutputs(threadId, runId, {
        tool_outputs: toolOutputs
      });
      
      // Recursively check status until complete
      return checkRunStatus(threadId, runId, onToolCall);
    }
    
    // If the run is completed, fetch the messages
    if (run.status === 'completed') {
      const messages = await openai.beta.threads.messages.list(threadId);
      
      // Convert to our internal format
      const formattedMessages: AssistantMessage[] = messages.data.map(msg => ({
        role: msg.role as 'assistant' | 'user' | 'system',
        content: msg.content[0].type === 'text' ? msg.content[0].text.value : ''
      }));
      
      return { status: run.status, messages: formattedMessages };
    }
    
    // Handle in-progress or failed states
    return { status: run.status, messages: [] };
  } catch (error) {
    console.error('Error checking run status:', error);
    throw new Error('Failed to check assistant run status');
  }
}

/**
 * Update the assistant with new business data
 * @param assistantId Assistant ID to update
 * @param instructions New instructions for the assistant
 * @param tools Tools configuration for the assistant
 * @returns Updated assistant data
 */
export async function updateAssistantConfiguration(
  assistantId: string = ASSISTANT_ID,
  instructions?: string,
  tools?: any[]
): Promise<any> {
  try {
    const assistant = await openai.beta.assistants.retrieve(assistantId);
    
    // Prepare update params
    const updateParams: any = {};
    if (instructions) {
      updateParams.instructions = instructions;
    }
    if (tools) {
      updateParams.tools = tools;
    }
    
    // Only update if there are changes
    if (Object.keys(updateParams).length > 0) {
      return await openai.beta.assistants.update(assistantId, updateParams);
    }
    
    return assistant;
  } catch (error) {
    console.error('Error updating assistant configuration:', error);
    throw new Error('Failed to update assistant configuration');
  }
}

/**
 * Generate system instructions for the assistant based on current business context
 * @param businessContext Current business context data
 * @returns Formatted instructions for the assistant
 */
export function generateSystemInstructions(businessContext: AIDataContext): string {
  // Calculate key metrics to highlight
  const revenueGrowth = businessContext.salesTrends.growthRate.toFixed(2);
  const stockoutCount = businessContext.inventoryHealth.stockouts;
  const atRiskCount = businessContext.inventoryHealth.atRisk;
  
  // Format top products
  const topProductsList = businessContext.productInsights.topProducts
    .map(p => `- ${p.name}: $${p.revenue.toFixed(2)} (${p.growth > 0 ? '+' : ''}${p.growth.toFixed(2)}%)`)
    .join('\n');
  
  // Format underperforming products
  const underperformersList = businessContext.productInsights.underperformers
    .map(p => `- ${p.name}: $${p.revenue.toFixed(2)} (${p.growth.toFixed(2)}%)`)
    .join('\n');
  
  // Generate the instructions
  return `
  You are an AI business analyst for ProHandel, a retail management system.
  
  CURRENT BUSINESS CONTEXT:
  - Revenue Growth Rate: ${revenueGrowth}%
  - Inventory Health: ${stockoutCount} stockouts, ${atRiskCount} at risk
  
  TOP PERFORMING PRODUCTS:
  ${topProductsList}
  
  UNDERPERFORMING PRODUCTS:
  ${underperformersList}
  
  YOUR ROLE:
  1. Answer questions about business performance, sales trends, and inventory health
  2. Provide actionable insights based on the data
  3. Recommend strategies to improve sales and reduce stockouts
  4. Analyze patterns and correlations in the data
  5. Compare performance across warehouses and categories
  
  When answering questions:
  - Reference specific data points to support your analysis
  - Provide clear, actionable recommendations
  - Highlight both positive trends and areas of concern
  - Consider seasonal factors and industry context
  - Be concise but thorough
  
  The user will provide you with their questions, and you'll have access to additional
  context data via special messages. Don't reference these context messages directly,
  just use the information to inform your responses.
  `;
}

/**
 * Define custom function tools for the assistant
 */
export const ASSISTANT_TOOLS = [
  {
    type: "function",
    function: {
      name: "get_warehouse_details",
      description: "Get detailed information about a specific warehouse",
      parameters: {
        type: "object",
        properties: {
          warehouse_id: {
            type: "string",
            description: "The ID of the warehouse to get details for"
          }
        },
        required: ["warehouse_id"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "get_product_details",
      description: "Get detailed information about a specific product",
      parameters: {
        type: "object",
        properties: {
          product_id: {
            type: "string",
            description: "The ID of the product to get details for"
          }
        },
        required: ["product_id"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "get_category_performance",
      description: "Get performance metrics for a specific product category",
      parameters: {
        type: "object",
        properties: {
          category_id: {
            type: "string",
            description: "The ID of the category to analyze"
          },
          period: {
            type: "string",
            enum: ["7d", "30d", "90d"],
            description: "Time period for the analysis"
          }
        },
        required: ["category_id"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "generate_inventory_recommendations",
      description: "Generate specific recommendations for improving inventory management",
      parameters: {
        type: "object",
        properties: {
          warehouse_id: {
            type: "string",
            description: "The ID of the warehouse to generate recommendations for"
          },
          risk_threshold: {
            type: "number",
            description: "Risk threshold (low = more recommendations, high = fewer)"
          }
        },
        required: ["warehouse_id"]
      }
    }
  }
];
