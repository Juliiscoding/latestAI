import type { NextApiRequest, NextApiResponse } from 'next';

// Environment variables
const MCP_API_URL = process.env.NEXT_PUBLIC_MCP_API_URL || 'http://localhost:3001';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const TENANT_ID = process.env.TENANT_ID;

// Response type
type MCPResponse = {
  response: string;
  answer?: string;
  sources?: any[];
  error?: string;
  debug?: any;
};

/**
 * MCP API Middleware
 * Connects our frontend requests to the MCP server with proper authentication and tenant context
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<MCPResponse>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ response: '', error: 'Method not allowed' });
  }

  try {
    const { prompt, context } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ response: '', error: 'Prompt is required' });
    }

    // Ensure tenant ID is included in context
    const enrichedContext = {
      ...context,
      tenant: TENANT_ID,
      timestamp: new Date().toISOString()
    };

    console.log(`Processing MCP request: ${prompt}`);
    console.log(`Context: ${JSON.stringify(enrichedContext)}`);
    
    // Call the MCP API
    const mcpResponse = await fetch(`${MCP_API_URL}/api/v1/tools/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'X-Tenant-ID': TENANT_ID || ''
      },
      body: JSON.stringify({
        prompt,
        context: enrichedContext,
        tools: [
          "sales_by_warehouse",
          "inventory_levels",
          "product_performance",
          "stockout_risk"
        ]
      })
    });
    
    if (!mcpResponse.ok) {
      const errorText = await mcpResponse.text();
      console.error(`MCP API error: ${mcpResponse.status} ${errorText}`);
      throw new Error(`MCP API error: ${mcpResponse.status} ${errorText}`);
    }
    
    const data = await mcpResponse.json();
    
    return res.status(200).json({
      response: data.response || data.answer || "The AI couldn't generate a response",
      sources: data.sources || [],
      debug: process.env.NODE_ENV === 'development' ? data.debug : undefined
    });
  } catch (error: any) {
    console.error('Error processing MCP request:', error);
    return res.status(500).json({
      response: '',
      error: `Error processing your request: ${error.message || 'Unknown error'}`
    });
  }
}
