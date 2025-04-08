import type { NextApiRequest, NextApiResponse } from 'next';
import { getAIAssistantContext } from '../../../lib/data/prohandel';
import { fetchMcpResponseWithCache, hashForCacheKey } from '../../../lib/utils/cacheUtils';

// Environment variables
const MCP_API_URL = process.env.NEXT_PUBLIC_MCP_API_URL || 'http://localhost:3001';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const OPENAI_ASSISTANT_ID = process.env.OPENAI_ASSISTANT_ID;
const TENANT_ID = process.env.TENANT_ID;
const USE_REAL_MCP = process.env.NEXT_PUBLIC_USE_REAL_MCP === 'true';

// Configure streaming
export const config = {
  api: {
    responseLimit: false,
    bodyParser: {
      sizeLimit: '1mb',
    },
  },
};

// Define response types
interface AIStreamingResponse {
  done: boolean;
  content?: string;
  error?: string;
  sources?: any[];
}

/**
 * Handles AI assistant queries with streaming responses
 * Supports both MCP and direct OpenAI API fallback
 */
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Parse request body
  const { question, warehouseId, userId, stream = true } = req.body;
  
  if (!question) {
    return res.status(400).json({ error: 'Question is required' });
  }

  // Set up streaming response headers if streaming is requested
  if (stream) {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
  }

  // Track if the response has ended to prevent sending after close
  let hasEnded = false;
  res.on('close', () => {
    hasEnded = true;
  });

  // Helper to send a streaming event
  const sendStreamEvent = (data: AIStreamingResponse) => {
    if (!hasEnded && stream) {
      res.write(`data: ${JSON.stringify(data)}\n\n`);
      
      // End the response when done
      if (data.done && !hasEnded) {
        hasEnded = true;
        res.end();
      }
    }
  };

  try {
    // Start by sending a loading event
    sendStreamEvent({ done: false, content: '' });

    // Get AI context with tenant-aware data
    console.log(`Processing AI request for warehouse: ${warehouseId}`);
    const context = await getAIAssistantContext(warehouseId, true);
    
    if (!context && warehouseId) {
      sendStreamEvent({ 
        done: false, 
        content: 'Loading context data for this warehouse...'
      });
    }

    // Prepare MCP request with tenant context
    const mcpRequest = {
      prompt: question,
      context: {
        tenant: TENANT_ID,
        warehouseId: warehouseId || 'all',
        userId: userId || 'anonymous',
        salesTrends: context?.salesTrends,
        inventoryHealth: context?.inventoryHealth,
        productInsights: context?.productInsights,
        timestamp: new Date().toISOString(),
      },
      assistantId: OPENAI_ASSISTANT_ID,
      stream: true, // Request streaming from MCP
    };

    // Create a deterministic cache key from the request
    const cacheKey = `question:${hashForCacheKey(question)}:warehouse:${warehouseId || 'all'}`;

    if (USE_REAL_MCP) {
      try {
        // Use cache-wrapped fetch for MCP API
        const mcpData = await fetchMcpResponseWithCache(
          async () => {
            // Try calling MCP endpoint
            sendStreamEvent({ 
              done: false, 
              content: 'Analyzing your business data...' 
            });
            
            console.log(`Calling MCP API at ${MCP_API_URL}/api/v1/tools/execute`);
            
            if (stream) {
              // For streaming, we need to handle the response differently
              const mcpResponse = await fetch(`${MCP_API_URL}/api/v1/tools/execute`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${OPENAI_API_KEY}`,
                  'X-Tenant-ID': TENANT_ID || '',
                  'Accept': 'text/event-stream',
                },
                body: JSON.stringify(mcpRequest),
              });

              if (!mcpResponse.ok) {
                throw new Error(`MCP API error: ${mcpResponse.status}`);
              }

              // Handle streaming response from MCP
              const reader = mcpResponse.body?.getReader();
              if (!reader) throw new Error('Failed to get response reader');

              let result = '';
              let decoder = new TextDecoder();

              // Process the stream chunk by chunk
              while (!hasEnded) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n\n');
                
                for (const line of lines) {
                  if (line.startsWith('data: ')) {
                    try {
                      const data = JSON.parse(line.slice(6));
                      if (data.content) {
                        result += data.content;
                        sendStreamEvent({ 
                          done: false, 
                          content: result,
                          sources: data.sources
                        });
                      }
                      if (data.done) {
                        sendStreamEvent({ 
                          done: true, 
                          content: result,
                          sources: data.sources 
                        });
                        return { response: result, sources: data.sources };
                      }
                    } catch (e) {
                      // Skip invalid JSON
                    }
                  }
                }
              }
              
              return { response: result, sources: [] };
            } else {
              // Non-streaming request
              const mcpResponse = await fetch(`${MCP_API_URL}/api/v1/tools/execute`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${OPENAI_API_KEY}`,
                  'X-Tenant-ID': TENANT_ID || '',
                },
                body: JSON.stringify({...mcpRequest, stream: false}),
              });

              if (!mcpResponse.ok) {
                throw new Error(`MCP API error: ${mcpResponse.status}`);
              }

              return await mcpResponse.json();
            }
          },
          cacheKey,
          false // Don't force fresh by default
        );

        // For non-streaming, return the full response
        if (!stream) {
          return res.status(200).json({
            answer: mcpData.response || mcpData.answer,
            sources: mcpData.sources || [],
          });
        }
        
        // Streaming is handled within the fetchMcpResponseWithCache function
        
      } catch (mcpError) {
        console.error('MCP API error, falling back to OpenAI:', mcpError);
        sendStreamEvent({ 
          done: false, 
          content: 'Analyzing with backup system...' 
        });
        
        // Fall back to OpenAI direct call
        await handleOpenAIFallback(question, context, sendStreamEvent, stream, res);
      }
    } else {
      // Use OpenAI directly if MCP is disabled
      await handleOpenAIFallback(question, context, sendStreamEvent, stream, res);
    }
  } catch (error: any) {
    console.error('Error processing AI request:', error);
    
    if (stream) {
      sendStreamEvent({ 
        done: true, 
        error: `Error processing your request: ${error.message || 'Unknown error'}` 
      });
    } else {
      return res.status(500).json({
        error: `Error processing your request: ${error.message || 'Unknown error'}`
      });
    }
  }
}

/**
 * Fallback handler for direct OpenAI calls when MCP is unavailable
 */
async function handleOpenAIFallback(
  question: string,
  context: any,
  sendStreamEvent: (data: AIStreamingResponse) => void,
  stream: boolean,
  res: NextApiResponse
) {
  // Format the context data into a readable prompt
  const systemPrompt = `
You are an AI assistant for ProHandel, a B2B warehouse management system.
You help users analyze their sales and inventory data to make better business decisions.

Current context:
- Warehouse: ${context?.warehouseId || 'All warehouses'}
- Sales trends: 
  * Last 7 days: €${context?.salesTrends?.last7d || 0}
  * Last 30 days: €${context?.salesTrends?.last30d || 0}
  * Last 90 days: €${context?.salesTrends?.last90d || 0}
  * Growth rate: ${context?.salesTrends?.growthRate || 0}%
- Inventory health:
  * Stockouts: ${context?.inventoryHealth?.stockouts || 0} products
  * At risk: ${context?.inventoryHealth?.atRisk || 0} products
  * Stable: ${context?.inventoryHealth?.stable || 0} products
- Top products:
  * ${context?.productInsights?.topProducts?.map((p: any) => 
      `${p.name}: €${p.revenue} (${p.growth > 0 ? '+' : ''}${p.growth}%)`
    ).join('\n  * ') || 'No data'}

Answer the user's question about their business based on this context.
Keep your response concise, professional, and action-oriented.
`;

  try {
    if (stream) {
      // Stream response from OpenAI
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OPENAI_API_KEY}`
        },
        body: JSON.stringify({
          model: 'gpt-4-turbo',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: question }
          ],
          stream: true
        })
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('Failed to get response reader');

      let fullResponse = '';
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ') && line !== 'data: [DONE]') {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.choices && data.choices[0]?.delta?.content) {
                fullResponse += data.choices[0].delta.content;
                sendStreamEvent({ done: false, content: fullResponse });
              }
            } catch (e) {
              // Skip invalid JSON
            }
          } else if (line === 'data: [DONE]') {
            sendStreamEvent({ done: true, content: fullResponse });
            return;
          }
        }
      }
    } else {
      // Non-streaming response
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OPENAI_API_KEY}`
        },
        body: JSON.stringify({
          model: 'gpt-4-turbo',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: question }
          ],
          temperature: 0.7,
          max_tokens: 500
        })
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.status}`);
      }

      const data = await response.json();
      res.status(200).json({
        answer: data.choices[0].message.content,
        sources: []
      });
    }
  } catch (error) {
    console.error('OpenAI fallback error:', error);
    sendStreamEvent({ 
      done: true, 
      error: `AI processing error: ${error instanceof Error ? error.message : 'Unknown error'}` 
    });
  }
}
