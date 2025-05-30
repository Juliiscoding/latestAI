'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Loader2 } from 'lucide-react';

/**
 * InsightsComponent
 * 
 * Komponente zur Anzeige von automatischen Business-Insights aus dem RAG-System
 */
export default function InsightsComponent() {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const response = await axios.get('/api/rag/insights');
        setInsights(response.data);
      } catch (err) {
        console.error('Error fetching insights:', err);
        setError(err.response?.data?.error || 'Fehler beim Laden der Insights');
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-40">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-600 rounded-md">
        {error}
      </div>
    );
  }

  if (!insights || !insights.insights || Object.keys(insights.insights).length === 0) {
    return (
      <div className="p-4 bg-yellow-50 text-yellow-700 rounded-md">
        Keine Insights verfügbar. Stellen Sie sicher, dass Ihre Daten korrekt indiziert sind.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Business Insights</h2>
        <div className="text-sm text-gray-500">
          Stand: {new Date(insights.timestamp).toLocaleString()}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(insights.insights).map(([key, insight]) => (
          <Card key={key} className="h-full">
            <CardHeader>
              <CardTitle className="text-lg">{insight.question}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-line">{insight.answer}</p>
              
              {insight.sources && insight.sources.length > 0 && (
                <div className="mt-4">
                  <details>
                    <summary className="text-sm text-primary cursor-pointer">
                      Quellen anzeigen
                    </summary>
                    <div className="mt-2 space-y-2">
                      {insight.sources.slice(0, 3).map((source, index) => (
                        <div key={index} className="text-xs p-2 bg-gray-50 rounded border border-gray-200">
                          <div className="text-gray-600">
                            {source.text.substring(0, 100)}...
                          </div>
                          <div className="mt-1 text-gray-400 flex justify-between">
                            <span>Quelle: {source.metadata.source || 'Unbekannt'}</span>
                            <span>Relevanz: {Math.round(source.score * 100)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
