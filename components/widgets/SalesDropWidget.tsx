import React, { useState, useEffect } from 'react';
import { 
  SalesDropAnalysisParams, 
  SalesDropAnalysisResult 
} from '../../lib/mcp/prompts/salesDropAnalysis';
import { fetchMcpResponseWithCache } from '../../lib/utils/cacheUtils';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Button } from "../ui/button";
import { AlertCircle, AlertTriangle, CheckCircle, RefreshCw, TrendingDown } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Badge } from "../ui/badge";
import { Skeleton } from "../ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";

const DEFAULT_PARAMS: SalesDropAnalysisParams = {
  timeframe: 'monthly',
  comparisonType: 'previous_period',
  minDropPercentage: 5,
};

const SEVERITY_CONFIG = {
  low: { color: '#22c55e', icon: CheckCircle, text: 'Low' },
  medium: { color: '#eab308', icon: AlertTriangle, text: 'Medium' },
  high: { color: '#f97316', icon: AlertTriangle, text: 'High' },
  critical: { color: '#ef4444', icon: AlertCircle, text: 'Critical' },
};

/**
 * Intelligent Widget: Sales Drop Analysis
 * 
 * A specialized widget that provides analysis and recommendations
 * for sales drops across different timeframes and categories.
 */
export default function SalesDropWidget({ 
  warehouseId,
  tenant,
  onRefresh
}: { 
  warehouseId?: string;
  tenant: string;
  onRefresh?: () => void;
}) {
  const [params, setParams] = useState<SalesDropAnalysisParams>(DEFAULT_PARAMS);
  const [analysisResult, setAnalysisResult] = useState<SalesDropAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Function to fetch analysis from MCP
  const fetchAnalysis = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    
    try {
      // Construct contextData object - this would normally come from your data hooks
      const contextData = {
        tenant,
        warehouseId: warehouseId || 'all',
        timestamp: new Date().toISOString(),
      };
      
      // Unique cache key based on parameters and warehouse
      const cacheKey = `sales_drop:${warehouseId || 'all'}:${params.timeframe}:${params.comparisonType}`;
      
      // Call the MCP API with caching
      const result = await fetchMcpResponseWithCache<SalesDropAnalysisResult>(
        async () => {
          // For simplicity in this example, we're just calling our local API
          // In production, you'd call your deployed MCP API directly
          const response = await fetch('/api/mcp/analyze-sales-drop', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              params,
              context: contextData,
              forceFresh: forceRefresh
            }),
          });
          
          if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
          }
          
          return response.json();
        },
        cacheKey,
        30 * 60 // 30 minute TTL
      );
      
      setAnalysisResult(result);
    } catch (err: any) {
      console.error('Error fetching sales drop analysis:', err);
      setError(err.message || 'Failed to fetch analysis');
    } finally {
      setLoading(false);
    }
  };
  
  // Initial fetch when the component mounts
  useEffect(() => {
    fetchAnalysis();
  }, [warehouseId, params.timeframe, params.comparisonType]);
  
  // Get severity config
  const getSeverityConfig = (severity: string) => {
    return SEVERITY_CONFIG[severity as keyof typeof SEVERITY_CONFIG] || SEVERITY_CONFIG.medium;
  };
  
  // Prepare chart data
  const chartData = analysisResult?.topFactors?.map(factor => ({
    name: factor.factor,
    value: factor.impact,
    fill: getSeverityConfig(analysisResult.overview.severity).color,
  })) || [];
  
  // If we have categories data, prepare it for a chart
  const categoryData = analysisResult?.affectedCategories?.map(cat => ({
    name: cat.categoryName,
    value: cat.dropPercentage,
    previousValue: cat.previousValue,
    currentValue: cat.currentValue,
  })) || [];

  return (
    <Card className="w-full shadow-md">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-red-500" />
              Sales Drop Analysis
            </CardTitle>
            <CardDescription>
              Identifying revenue decline patterns and opportunities
            </CardDescription>
          </div>
          
          <div className="flex items-center gap-2">
            <Select
              value={params.timeframe}
              onValueChange={(value) => 
                setParams({...params, timeframe: value as any})
              }
            >
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Timeframe" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="quarterly">Quarterly</SelectItem>
              </SelectContent>
            </Select>
            
            <Select 
              value={params.comparisonType}
              onValueChange={(value) => 
                setParams({...params, comparisonType: value as any})
              }
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Comparison" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="previous_period">Previous Period</SelectItem>
                <SelectItem value="previous_year">Previous Year</SelectItem>
                <SelectItem value="custom">Custom Period</SelectItem>
              </SelectContent>
            </Select>
            
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => {
                fetchAnalysis(true);
                onRefresh?.();
              }}
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {error ? (
          <div className="p-4 text-center text-red-500">
            <AlertCircle className="h-10 w-10 mx-auto mb-2" />
            <p>{error}</p>
            <Button 
              variant="outline" 
              className="mt-2"
              onClick={() => fetchAnalysis(true)}
            >
              Try Again
            </Button>
          </div>
        ) : loading && !analysisResult ? (
          <div className="space-y-4">
            <Skeleton className="h-[40px] w-full" />
            <Skeleton className="h-[200px] w-full" />
            <Skeleton className="h-[100px] w-full" />
          </div>
        ) : analysisResult ? (
          <Tabs 
            value={activeTab} 
            onValueChange={setActiveTab}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="factors">Contributing Factors</TabsTrigger>
              <TabsTrigger value="categories">Affected Categories</TabsTrigger>
              <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-4 mt-4">
              <div className="flex items-center justify-between p-4 border rounded-lg bg-slate-50">
                <div>
                  <h3 className="text-2xl font-bold">
                    {analysisResult.overview.dropPercentage.toFixed(1)}%
                  </h3>
                  <p className="text-sm text-slate-500">
                    Sales drop in {analysisResult.overview.timeframe}
                  </p>
                  <p className="text-xs text-slate-400">
                    vs {analysisResult.overview.comparisonPeriod}
                  </p>
                </div>
                
                <div>
                  {(() => {
                    const { color, icon: Icon, text } = getSeverityConfig(analysisResult.overview.severity);
                    return (
                      <div className="text-center">
                        <Badge 
                          style={{backgroundColor: color}}
                          className="mb-1 text-white"
                        >
                          {text} Severity
                        </Badge>
                        <div className="flex justify-center">
                          <Icon 
                            style={{color}} 
                            className="h-10 w-10" 
                          />
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>
              
              <div className="border rounded-lg p-4">
                <h3 className="font-medium mb-2">Key Insights</h3>
                <ul className="space-y-2">
                  {analysisResult.relatedInsights.map((insight, i) => (
                    <li key={i} className="text-sm flex items-start gap-2">
                      <span className="bg-blue-100 rounded-full p-1 mt-0.5">
                        <AlertCircle className="h-3 w-3 text-blue-600" />
                      </span>
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
            </TabsContent>
            
            <TabsContent value="factors" className="space-y-4 mt-4">
              <div className="border rounded-lg p-4">
                <h3 className="font-medium mb-4">Top Contributing Factors</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={chartData} layout="vertical">
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis type="category" dataKey="name" width={150} />
                    <Tooltip 
                      formatter={(value) => [`${value}% Impact`, 'Contribution']}
                    />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              
              <div className="border rounded-lg p-4">
                <h3 className="font-medium mb-2">Factor Details</h3>
                <div className="space-y-3">
                  {analysisResult.topFactors.map((factor, i) => (
                    <div key={i} className="border-b pb-2 last:border-0">
                      <div className="flex justify-between">
                        <span className="font-medium">{factor.factor}</span>
                        <Badge>
                          {factor.impact}% Impact
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-600 mt-1">
                        {factor.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="categories" className="space-y-4 mt-4">
              <div className="border rounded-lg p-4">
                <h3 className="font-medium mb-4">Affected Categories</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={categoryData}>
                    <XAxis dataKey="name" />
                    <YAxis label={{ value: 'Drop %', angle: -90, position: 'insideLeft' }} />
                    <Tooltip formatter={(value) => [`${value}%`, 'Drop Percentage']} />
                    <Bar dataKey="value" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              
              <div className="border rounded-lg p-4">
                <h3 className="font-medium mb-2">Category Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {analysisResult.affectedCategories.map((category, i) => (
                    <div key={i} className="border rounded p-3">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{category.categoryName}</span>
                        <Badge 
                          variant={category.dropPercentage > 15 ? "destructive" : "secondary"}
                        >
                          {category.dropPercentage}% Drop
                        </Badge>
                      </div>
                      <div className="text-sm mt-2">
                        <div className="flex justify-between text-xs text-slate-500">
                          <span>Previous: €{category.previousValue.toLocaleString()}</span>
                          <span>Current: €{category.currentValue.toLocaleString()}</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2 mt-1">
                          <div 
                            className="bg-red-500 h-2 rounded-full" 
                            style={{ width: `${100 - category.dropPercentage}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="recommendations" className="mt-4">
              <div className="border rounded-lg p-4">
                <h3 className="font-medium mb-2">Recommended Actions</h3>
                <div className="space-y-3">
                  {analysisResult.recommendations.map((rec, i) => {
                    const priorityColor = {
                      high: 'bg-red-100 text-red-800',
                      medium: 'bg-yellow-100 text-yellow-800',
                      low: 'bg-green-100 text-green-800'
                    }[rec.priority];
                    
                    return (
                      <div key={i} className="flex gap-3 p-3 border rounded-lg hover:bg-slate-50">
                        <div className="mt-1">
                          <span className={`text-xs px-2 py-1 rounded-full ${priorityColor}`}>
                            {rec.priority}
                          </span>
                        </div>
                        <div>
                          <h4 className="font-medium">{rec.action}</h4>
                          <div className="flex gap-4 mt-1 text-xs text-slate-500">
                            <span>Impact: {rec.expectedImpact}</span>
                            <span>Timeframe: {rec.timeToImplement}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        ) : null}
      </CardContent>
      
      <CardFooter className="text-xs text-slate-500 pt-0">
        <div className="flex justify-between w-full">
          <span>
            Analysis time: {analysisResult ? new Date().toLocaleString() : '-'}
          </span>
          <span>
            Warehouse: {warehouseId || 'All warehouses'}
          </span>
        </div>
      </CardFooter>
    </Card>
  );
}
