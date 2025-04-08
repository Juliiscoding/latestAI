/**
 * Sales Drop Analysis Prompt for MCP
 * 
 * This structured prompt template is designed to analyze sales drops
 * across different time periods, product categories, and warehouses.
 * It generates insights with actionable recommendations.
 */
import { hashForCacheKey } from '../../utils/cacheUtils';

// Define the output schema for structured responses
export interface SalesDropAnalysisResult {
  overview: {
    dropPercentage: number;
    timeframe: string;
    comparisonPeriod: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
  };
  topFactors: Array<{
    factor: string;
    impact: number; // 0-100 percentage impact
    description: string;
  }>;
  affectedCategories: Array<{
    categoryName: string;
    dropPercentage: number;
    previousValue: number;
    currentValue: number;
  }>;
  recommendations: Array<{
    action: string;
    priority: 'low' | 'medium' | 'high';
    expectedImpact: string;
    timeToImplement: string;
  }>;
  relatedInsights: string[];
}

// Types for the request parameters
export interface SalesDropAnalysisParams {
  timeframe: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  comparisonType: 'previous_period' | 'previous_year' | 'custom';
  categoryFilter?: string[];
  warehouseId?: string;
  startDate?: string;
  endDate?: string;
  minDropPercentage?: number; // Only analyze drops greater than this percentage
}

/**
 * Generates a prompt for sales drop analysis with the MCP
 */
export function generateSalesDropAnalysisPrompt(
  params: SalesDropAnalysisParams,
  contextData: any
): { prompt: string; systemPrompt: string; cacheKey: string } {
  // Format the context data for the prompt
  const { 
    timeframe, 
    comparisonType, 
    categoryFilter, 
    warehouseId, 
    startDate, 
    endDate, 
    minDropPercentage = 5 
  } = params;
  
  // Build a cache key from the parameters
  const cacheKey = `sales_drop:${hashForCacheKey({
    timeframe,
    comparisonType,
    categoryFilter,
    warehouseId,
    startDate,
    endDate,
    minDropPercentage,
  })}`;
  
  // Create a detailed system prompt for the analysis
  const systemPrompt = `
You are a sales analytics expert for ProHandel, a B2B warehouse management system.
You're analyzing a sales drop for the ${timeframe} period ${startDate ? `from ${startDate} to ${endDate}` : ''}.
The comparison is against the ${comparisonType.replace('_', ' ')} data.

${categoryFilter ? `Focus on these categories: ${categoryFilter.join(', ')}.` : 'Analyze all product categories.'}
${warehouseId ? `Analyze data for warehouse ID: ${warehouseId}` : 'Analyze data across all warehouses.'}
Only report drops greater than ${minDropPercentage}%.

Your analysis should:
1. Quantify the overall sales drop percentage
2. Identify the top contributing factors
3. List the most affected product categories
4. Provide actionable recommendations
5. Include related insights about inventory or marketing impacts

You must follow this exact JSON structure for your response:
{
  "overview": {
    "dropPercentage": number,
    "timeframe": string,
    "comparisonPeriod": string,
    "severity": "low" | "medium" | "high" | "critical"
  },
  "topFactors": [
    {
      "factor": string,
      "impact": number,
      "description": string
    }
  ],
  "affectedCategories": [
    {
      "categoryName": string,
      "dropPercentage": number,
      "previousValue": number,
      "currentValue": number
    }
  ],
  "recommendations": [
    {
      "action": string,
      "priority": "low" | "medium" | "high",
      "expectedImpact": string,
      "timeToImplement": string
    }
  ],
  "relatedInsights": [string]
}
`;

  // Create a user prompt with the main analysis question
  const prompt = `
Analyze the sales drop in my ProHandel data with the following parameters:
- Timeframe: ${timeframe}
- Comparison: ${comparisonType.replace('_', ' ')}
${startDate ? `- Date range: ${startDate} to ${endDate}` : ''}
${categoryFilter ? `- Categories: ${categoryFilter.join(', ')}` : ''}
${warehouseId ? `- Warehouse: ${warehouseId}` : '- All warehouses'}

What is causing this sales drop and what should I do about it?
`;

  return {
    prompt,
    systemPrompt,
    cacheKey
  };
}

/**
 * Execute a sales drop analysis using the MCP API
 */
export async function executeSalesDropAnalysis(
  params: SalesDropAnalysisParams,
  contextData: any,
  mcpApiUrl: string,
  apiKey: string,
  tenantId: string
): Promise<SalesDropAnalysisResult> {
  const { prompt, systemPrompt, cacheKey } = generateSalesDropAnalysisPrompt(params, contextData);
  
  try {
    // Call the MCP API with our structured prompt
    const response = await fetch(`${mcpApiUrl}/api/v1/tools/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'X-Tenant-ID': tenantId
      },
      body: JSON.stringify({
        prompt,
        system_prompt: systemPrompt,
        context: {
          ...contextData,
          analysisParameters: params
        },
        tools: ["sales_data_analysis", "product_performance_analysis"],
        output_schema: {
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
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to execute sales drop analysis: ${response.status}`);
    }

    const data = await response.json();
    return data.response as SalesDropAnalysisResult;
  } catch (error) {
    console.error('Error executing sales drop analysis:', error);
    throw error;
  }
}

/**
 * Use this function to create a React component that displays
 * the sales drop analysis in a visually appealing way
 */
export function formatSalesDropAnalysisForDisplay(analysis: SalesDropAnalysisResult): string {
  // This is a simplified version for demonstration
  // In a real application, you would return JSX or React components
  
  // Helper to create a severity badge
  const getSeverityBadge = (severity: string) => {
    const colors = {
      low: '🟢 Low',
      medium: '🟡 Medium',
      high: '🟠 High', 
      critical: '🔴 Critical'
    };
    return colors[severity as keyof typeof colors] || severity;
  };
  
  // Format the recommendations section
  const formattedRecommendations = analysis.recommendations
    .map(rec => `- ${rec.action} (Priority: ${rec.priority}, Impact: ${rec.expectedImpact}, Timeframe: ${rec.timeToImplement})`)
    .join('\n');
  
  // Format affected categories
  const formattedCategories = analysis.affectedCategories
    .map(cat => `- ${cat.categoryName}: ${cat.dropPercentage.toFixed(1)}% drop (€${cat.previousValue.toFixed(0)} → €${cat.currentValue.toFixed(0)})`)
    .join('\n');
  
  // Create the formatted output
  return `
# Sales Drop Analysis

## Overview
📉 **${analysis.overview.dropPercentage.toFixed(1)}% drop** in ${analysis.overview.timeframe} vs ${analysis.overview.comparisonPeriod}
🚨 **Severity**: ${getSeverityBadge(analysis.overview.severity)}

## Top Contributing Factors
${analysis.topFactors.map((factor, i) => 
  `${i+1}. **${factor.factor}** (${factor.impact.toFixed(0)}% impact)\n   ${factor.description}`
).join('\n')}

## Most Affected Categories
${formattedCategories}

## Recommended Actions
${formattedRecommendations}

## Related Insights
${analysis.relatedInsights.map(insight => `- ${insight}`).join('\n')}
`;
}
