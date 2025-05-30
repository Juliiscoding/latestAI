'use client';

import { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Checkbox } from '../ui/checkbox';
import { Loader2, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import RAGErrorHandling from './RAGErrorHandling';
import RAGHelpPopover from './RAGHelpPopover';

/**
 * AdminIndexingComponent
 * 
 * Komponente für Administratoren zur Steuerung der Datenindexierung im RAG-System
 */
export default function AdminIndexingComponent() {
  const [indexing, setIndexing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [forceReindex, setForceReindex] = useState(false);

  /**
   * Startet den Indexierungsprozess
   */
  const handleIndexing = async () => {
    setIndexing(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await axios.post('/api/rag/index', { 
        force_reindex: forceReindex 
      });
      setResult(response.data);
    } catch (err) {
      console.error('Error during indexing:', err);
      setError(err.response?.data?.error || 'Fehler bei der Indexierung');
    } finally {
      setIndexing(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>Daten-Indexierung</CardTitle>
            <CardDescription>
              Starten Sie hier die Indexierung von Tenant-Daten für das RAG-System. 
              Die Indexierung kann einige Zeit in Anspruch nehmen, abhängig von der Datenmenge.
            </CardDescription>
          </div>
          <RAGHelpPopover type="admin" placement="bottom-end" />
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="flex items-center space-x-2">
          <Checkbox 
            id="force-reindex" 
            checked={forceReindex}
            onCheckedChange={setForceReindex}
            disabled={indexing}
          />
          <label 
            htmlFor="force-reindex" 
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            Neuindexierung erzwingen (bestehende Daten überschreiben)
          </label>
        </div>
        
        <Button 
          onClick={handleIndexing} 
          disabled={indexing}
          className="w-full"
        >
          {indexing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Indexierung läuft...
            </>
          ) : (
            'Daten indexieren'
          )}
        </Button>
        
        {error && (
          <RAGErrorHandling 
            error={error} 
            variant="inline" 
            onRetry={handleIndexing} 
          />
        )}
        
        {result && (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertTitle className="text-green-800">Indexierung gestartet</AlertTitle>
            <AlertDescription className="text-green-700">
              {result.message}
              <div className="mt-2 text-sm text-green-600">Status: {result.status}</div>
            </AlertDescription>
          </Alert>
        )}
        
        <div className="text-sm text-gray-500 p-4 bg-gray-50 rounded-md">
          <p className="font-semibold">Hinweis:</p>
          <p>Die Indexierung läuft im Hintergrund und kann je nach Datenmenge einige Zeit in Anspruch nehmen. 
             Sie können den Status der Indexierung später überprüfen.</p>
        </div>
      </CardContent>
    </Card>
  );
}
