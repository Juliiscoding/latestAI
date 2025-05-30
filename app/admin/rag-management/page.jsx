'use client';

import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import AdminIndexingComponent from '../../../components/mercurios/AdminIndexingComponent';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';

/**
 * RAG Management Admin Page
 * 
 * Admin-Seite für die Verwaltung des RAG-Systems, einschließlich Datenindexierung
 */
export default function RAGManagementPage() {
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

  // Überprüfen, ob der Benutzer ein Administrator ist
  if (!session.user.isAdmin) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-50 text-red-700 p-4 rounded-md">
          <h2 className="text-lg font-bold">Zugriff verweigert</h2>
          <p>Sie haben keine Berechtigung, auf diese Seite zuzugreifen. Diese Seite ist nur für Administratoren verfügbar.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">RAG-System-Verwaltung</h1>
        <p className="text-gray-500 mt-2">
          Verwalten Sie das Retrieval Augmented Generation (RAG) System
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <AdminIndexingComponent />
        
        <Card>
          <CardHeader>
            <CardTitle>RAG-System-Status</CardTitle>
            <CardDescription>
              Informationen über den aktuellen Status des RAG-Systems
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium">System-Konfiguration</h3>
                <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                  <div className="bg-gray-50 p-2 rounded">
                    <span className="font-medium">RAG-API-URL:</span>
                    <span className="ml-2 text-gray-600">{process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8000'}</span>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <span className="font-medium">LLM-Modell:</span>
                    <span className="ml-2 text-gray-600">Mistral Large</span>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <span className="font-medium">Embedding-Modell:</span>
                    <span className="ml-2 text-gray-600">BAAI/bge-m3</span>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <span className="font-medium">Datenquelle:</span>
                    <span className="ml-2 text-gray-600">S3 Data Lake</span>
                  </div>
                </div>
              </div>
              
              <div className="p-4 bg-blue-50 text-blue-700 rounded-md">
                <h3 className="font-medium">Hinweis</h3>
                <p className="mt-1 text-sm">
                  Die Datenindexierung läuft im Hintergrund und kann je nach Datenmenge einige Zeit in Anspruch nehmen.
                  Größere Datensätze können mehrere Minuten oder länger benötigen. Der Indexierungsstatus wird automatisch aktualisiert.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
