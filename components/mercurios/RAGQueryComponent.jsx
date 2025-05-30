'use client';

import { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Loader2 } from 'lucide-react';
import RAGErrorHandling from './RAGErrorHandling';
import RAGHelpPopover from './RAGHelpPopover';
import RAGQuerySuggestions from './RAGQuerySuggestions';

/**
 * RAGQueryComponent
 * 
 * Komponente zur Interaktion mit dem RAG-System durch Stellen von Fragen
 */
export default function RAGQueryComponent() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(true);

  /**
   * Verarbeitet eine ausgewählte Beispielfrage
   */
  const handleSuggestedQuery = (suggestedQuery) => {
    setQuestion(suggestedQuery);
    // Nach einer kurzen Verzögerung die Frage absenden
    setTimeout(() => {
      handleSubmit(new Event('submit'));
    }, 100);
    // Vorschläge ausblenden, wenn eine Frage ausgewählt wurde
    setShowSuggestions(false);
  };

  /**
   * Sendet eine Frage an die RAG-API
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!question.trim()) return;
    
    setLoading(true);
    setError(null);
    setShowSuggestions(false); // Vorschläge ausblenden, wenn eine Frage gestellt wird
    
    try {
      const response = await axios.post('/api/rag/ask', { question });
      setAnswer(response.data);
    } catch (err) {
      console.error('Error asking question:', err);
      setError(err.response?.data?.error || 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>Daten-Analyse</CardTitle>
            <CardDescription>
              Stellen Sie eine Frage zu Ihren Daten und erhalten Sie Antworten basierend auf Ihren Unternehmensquellen.
            </CardDescription>
          </div>
          <RAGHelpPopover type="query" placement="bottom-end" />
        </div>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center space-x-2">
            <Input
              type="text"
              placeholder="z.B. Wie hat sich der Umsatz im letzten Monat entwickelt?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="flex-1"
              disabled={loading}
              onFocus={() => !answer && setShowSuggestions(true)}
            />
            <Button type="submit" disabled={loading || !question.trim()}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Verarbeite...
                </>
              ) : (
                'Fragen'
              )}
            </Button>
          </div>
          
          {showSuggestions && !answer && !loading && (
            <RAGQuerySuggestions onSelectQuery={handleSuggestedQuery} />
          )}
          
          {!showSuggestions && !answer && !loading && (
            <div className="text-center mt-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setShowSuggestions(true)}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Beispielfragen anzeigen
              </Button>
            </div>
          )}
        </form>

        {error && (
          <div className="mt-4">
            <RAGErrorHandling 
              error={error} 
              variant="help" 
              onRetry={() => handleSubmit(new Event('submit'))} 
            />
          </div>
        )}

        {answer && (
          <div className="mt-4 space-y-4">
            <div className="p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium">Antwort:</h3>
              <p className="mt-2 whitespace-pre-line">{answer.answer}</p>
            </div>
            
            {answer.sources && answer.sources.length > 0 && (
              <div>
                <h3 className="font-medium mb-2">Quellen:</h3>
                <div className="space-y-2">
                  {answer.sources.map((source, index) => (
                    <div key={index} className="p-3 bg-gray-50 rounded-md border border-gray-200">
                      <p className="text-sm text-gray-600">
                        {source.text.length > 150 
                          ? `${source.text.substring(0, 150)}...` 
                          : source.text}
                      </p>
                      <div className="mt-1 text-xs text-gray-500 flex justify-between">
                        <span>Quelle: {source.metadata.source || 'Unbekannt'}</span>
                        <span>Relevanz: {Math.round(source.score * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
