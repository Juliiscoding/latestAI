import type { NextApiRequest, NextApiResponse } from 'next';
import { fetchMcpResponseWithCache } from '../../../lib/utils/cacheUtils';
import type { SalesDropAnalysisParams, SalesDropAnalysisResult } from '../../../lib/mcp/prompts/salesDropAnalysis';

// Environment variables
const MCP_API_URL = process.env.NEXT_PUBLIC_MCP_API_URL || 'https://mcp.mercurios.ai';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const TENANT_ID = process.env.TENANT_ID;

/**
 * API route handler for sales drop analysis
 * 
 * This endpoint calls the MCP with a structured prompt for sales drop analysis
 * and returns the formatted data for visualization in the widget
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { params, context } = req.body;

    if (!params) {
      return res.status(400).json({ error: 'Analysis parameters are required' });
    }

    // Merge context with additional data
    const enrichedContext = {
      ...context,
      tenant: context.tenant || TENANT_ID || 'default',
      timestamp: new Date().toISOString(),
    };

    // Generate a unique cache key based on parameters and context
    const cacheKeyPrefix = `sales_drop_analysis:${enrichedContext.tenant}:${enrichedContext.warehouseId || 'all'}`;
    const paramHash = Buffer.from(JSON.stringify(params)).toString('base64').substring(0, 10);
    const cacheKey = `${cacheKeyPrefix}:${paramHash}`;
    
    // Call MCP with caching
    const result = await fetchMcpResponseWithCache<SalesDropAnalysisResult>(
      async () => {
        console.log(`[${enrichedContext.tenant}] Fetching sales drop analysis from MCP`);
        
        // Create a structured system prompt
        const systemPrompt = generateSystemPrompt(params as SalesDropAnalysisParams);
        
        // Format the user prompt
        const userPrompt = `Analyze the sales drop in my business data using these parameters: 
        - Timeframe: ${params.timeframe}
        - Comparison type: ${params.comparisonType}
        ${params.categoryFilter ? `- Categories: ${params.categoryFilter.join(', ')}` : ''}
        ${params.warehouseId ? `- Warehouse: ${params.warehouseId}` : '- All warehouses'}
        
        What factors are causing this sales drop and what actionable steps should I take?`;
        
        // Prepare the request to the MCP API
        const mcpRequest = {
          prompt: userPrompt,
          system_prompt: systemPrompt,
          context: enrichedContext,
          tools: ["sales_data_analysis", "product_performance_analysis"],
          output_schema: generateOutputSchema()
        };
        
        // Call the MCP API
        const response = await fetch(`${MCP_API_URL}/api/v1/tools/execute`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${OPENAI_API_KEY}`,
            'X-Tenant-ID': enrichedContext.tenant
          },
          body: JSON.stringify(mcpRequest)
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error(`MCP API error: ${response.status}`, errorText);
          throw new Error(`MCP API error: ${response.status}`);
        }
        
        const data = await response.json();
        return data.response;
      },
      cacheKey,
      30 * 60 // 30 minute TTL
    );
    
    return res.status(200).json(result);
  } catch (error: any) {
    console.error('Error processing sales drop analysis:', error);
    return res.status(500).json({
      error: 'Failed to analyze sales data',
      message: error.message
    });
  }
}

/**
 * Generates a system prompt for the sales drop analysis
 */
function generateSystemPrompt(params: SalesDropAnalysisParams): string {
  return `
You are a sales analytics expert for ProHandel, a B2B warehouse management system.
You're analyzing a sales drop for the ${params.timeframe} period ${params.startDate ? `from ${params.startDate} to ${params.endDate}` : ''}.
The comparison is against the ${params.comparisonType.replace('_', ' ')} data.

${params.categoryFilter ? `Focus on these categories: ${params.categoryFilter.join(', ')}.` : 'Analyze all product categories.'}
${params.warehouseId ? `Analyze data for warehouse ID: ${params.warehouseId}` : 'Analyze data across all warehouses.'}
Only report drops greater than ${params.minDropPercentage || 5}%.

Your analysis should:
1. Quantify the overall sales drop percentage
2. Identify the top contributing factors
3. List the most affected product categories
4. Provide actionable recommendations
5. Include related insights about inventory or marketing impacts

Return results in the JSON format specified by the output_schema.`;
}

/**
 * Generates the output schema for structured MCP responses
 */
function generateOutputSchema() {
  return {
    type: "object",
    properties: {
      overview: {
        type: "object",
        properties: {
          dropPercentage: { type: "number" },
          timeframe: { type: "string" },
          comparisonPeriod: { type: "string" },
          severity: { type: "string", enum: ["low", "medium", "high", "critical"] }
        },
        required: ["dropPercentage", "timeframe", "comparisonPeriod", "severity"]
      },
      topFactors: {
        type: "array",
        items: {
          type: "object",
          properties: {
            factor: { type: "string" },
            impact: { type: "number" },
            description: { type: "string" }
          },
          required: ["factor", "impact", "description"]
        }
      },
      affectedCategories: {
        type: "array",
        items: {
          type: "object",
          properties: {
            categoryName: { type: "string" },
            dropPercentage: { type: "number" },
            previousValue: { type: "number" },
            currentValue: { type: "number" }
          },
          required: ["categoryName", "dropPercentage", "previousValue", "currentValue"]
        }
      },
      recommendations: {
        type: "array",
        items: {
          type: "object",
          properties: {
            action: { type: "string" },
            priority: { type: "string", enum: ["low", "medium", "high"] },
            expectedImpact: { type: "string" },
            timeToImplement: { type: "string" }
          },
          required: ["action", "priority", "expectedImpact", "timeToImplement"]
        }
      },
      relatedInsights: {
        type: "array",
        items: { type: "string" }
      }
    },
    required: ["overview", "topFactors", "affectedCategories", "recommendations", "relatedInsights"]
  };
}
