'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Send, Brain, Lightbulb, BarChart3, AlertTriangle } from 'lucide-react';
import { analyzeStockoutRisk, askInventoryQuestion, predictStockoutDates, getInventoryRecommendations } from '@/lib/openai/assistant';
import { useStockoutRisk } from '@/lib/hooks/use-prohandel-data';
import { cn } from '@/lib/utils';

interface AIInsightsWidgetProps {
  className?: string;
  useRealData?: boolean;
  warehouseId?: string | null;
}

export default function AIInsightsWidget({ 
  className = '',
  useRealData = false,
  warehouseId = null
}: AIInsightsWidgetProps) {
  const [activeTab, setActiveTab] = useState('insights');
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState<string | null>(null);
  const [analysisType, setAnalysisType] = useState<'insights' | 'predictions' | 'recommendations'>('insights');
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch stockout data to provide as context to the assistant
  const { data: stockoutData, isLoading: isLoadingStockout } = useStockoutRisk({ 
    useRealData,
    warehouseId
  });

  // Handle question submission
  const handleSubmitQuestion = async () => {
    if (!question.trim()) return;
    
    setIsLoading(true);
    setAiResponse(null);
    
    try {
      const response = await askInventoryQuestion(question, stockoutData?.data || []);
      setAiResponse(response);
    } catch (error) {
      console.error('Error getting AI response:', error);
      setAiResponse('Sorry, I encountered an error while processing your question. Please try again later.');
    } finally {
      setIsLoading(false);
      setQuestion('');
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  };

  // Handle analysis request
  const handleRequestAnalysis = async (type: 'insights' | 'predictions' | 'recommendations') => {
    setAnalysisType(type);
    setIsLoading(true);
    setAiResponse(null);
    
    try {
      let response = '';
      
      switch (type) {
        case 'insights':
          response = await analyzeStockoutRisk(stockoutData?.data || []);
          break;
        case 'predictions':
          response = await predictStockoutDates(stockoutData?.data || [], []); // Need to add sales data
          break;
        case 'recommendations':
          response = await getInventoryRecommendations(stockoutData?.data || [], []); // Need to add sales data
          break;
      }
      
      setAiResponse(response);
    } catch (error) {
      console.error('Error getting AI analysis:', error);
      setAiResponse('Sorry, I encountered an error while generating insights. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  // Format AI response with markdown
  const formatResponse = (response: string) => {
    // Simple markdown formatting
    return response
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '<br/><br/>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <Card className={cn(className, "w-full")}>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Brain className="mr-2 h-5 w-5 text-primary" />
          AI Inventory Insights
        </CardTitle>
        <CardDescription>
          Ask questions about your inventory or get AI-powered insights
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-2 mb-4">
            <TabsTrigger value="insights">
              <Lightbulb className="mr-2 h-4 w-4" />
              AI Insights
            </TabsTrigger>
            <TabsTrigger value="ask">
              <Send className="mr-2 h-4 w-4" />
              Ask a Question
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="insights" className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <Button 
                variant={analysisType === 'insights' ? "default" : "outline"} 
                className="flex flex-col items-center justify-center h-24 space-y-2"
                onClick={() => handleRequestAnalysis('insights')}
              >
                <AlertTriangle className="h-8 w-8" />
                <span>Stockout Insights</span>
              </Button>
              <Button 
                variant={analysisType === 'predictions' ? "default" : "outline"} 
                className="flex flex-col items-center justify-center h-24 space-y-2"
                onClick={() => handleRequestAnalysis('predictions')}
              >
                <BarChart3 className="h-8 w-8" />
                <span>Stock Predictions</span>
              </Button>
              <Button 
                variant={analysisType === 'recommendations' ? "default" : "outline"} 
                className="flex flex-col items-center justify-center h-24 space-y-2"
                onClick={() => handleRequestAnalysis('recommendations')}
              >
                <Lightbulb className="h-8 w-8" />
                <span>Recommendations</span>
              </Button>
            </div>
          </TabsContent>
          
          <TabsContent value="ask" className="space-y-4">
            <div className="flex space-x-2">
              <Input
                ref={inputRef}
                placeholder="Ask about your inventory (e.g., 'Which products are trending down?')"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSubmitQuestion()}
                className="flex-1"
              />
              <Button onClick={handleSubmitQuestion} disabled={isLoading || !question.trim()}>
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
            <div className="text-sm text-muted-foreground">
              <p>Example questions:</p>
              <ul className="list-disc pl-5 space-y-1 mt-1">
                <li>Which products are at highest risk of stocking out?</li>
                <li>How many days until my top-selling product runs out?</li>
                <li>What inventory should I reorder this week?</li>
              </ul>
            </div>
          </TabsContent>
        </Tabs>
        
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-8 space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">
              {activeTab === 'insights' 
                ? `Analyzing your inventory ${analysisType}...` 
                : 'Processing your question...'}
            </p>
          </div>
        ) : aiResponse ? (
          <div className="mt-6 p-4 bg-muted/50 rounded-md">
            <div 
              className="prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: formatResponse(aiResponse) }}
            />
          </div>
        ) : null}
      </CardContent>
      <CardFooter className="text-xs text-muted-foreground">
        Powered by OpenAI Assistants API
      </CardFooter>
    </Card>
  );
}
