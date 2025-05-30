'use client';

import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import RAGQueryComponent from '../../../components/mercurios/RAGQueryComponent';
import InsightsComponent from '../../../components/mercurios/InsightsComponent';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';

/**
 * RAG Intelligence Dashboard Page
 * 
 * Seite für die Interaktion mit dem RAG-System und Anzeige von Business Insights
 */
export default function RAGIntelligencePage() {
  const { data: session, status } = useSession();
  
  // Weiterleitung zur Login-Seite, wenn nicht authentifiziert
  if (status === 'unauthenticated') {
    redirect('/login');
  }

  // Während der Überprüfung der Authentifizierung anzeigen
  if (status === 'loading') {
    return (
      <div className="flex justify-center items-center h-screen">
        <p className="text-lg">Lade...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Business Intelligence</h1>
        <p className="text-gray-500 mt-2">
          Fragen Sie Ihre Daten und entdecken Sie KI-generierte Erkenntnisse
        </p>
      </div>

      <Tabs defaultValue="query" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="query">Daten abfragen</TabsTrigger>
          <TabsTrigger value="insights">Business Insights</TabsTrigger>
        </TabsList>
        
        <TabsContent value="query" className="space-y-6">
          <RAGQueryComponent />
        </TabsContent>
        
        <TabsContent value="insights" className="space-y-6">
          <InsightsComponent />
        </TabsContent>
      </Tabs>
    </div>
  );
}
