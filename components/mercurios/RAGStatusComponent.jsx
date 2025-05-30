'use client';

import React, { useState, useEffect } from 'react';
import { RAGClient } from '../../lib/mercurios/clients/ragClient';
import { useSession } from 'next-auth/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { AlertCircle, CheckCircle } from 'lucide-react';

/**
 * RAGStatusComponent
 * 
 * Diese Komponente zeigt den aktuellen Status des RAG-Systems an, einschließlich:
 * - Verbindungsstatus zum RAG-API-Server
 * - Anzahl der indexierten Dokumente pro Tenant
 * - Letzte Indexierungszeit
 * - Embedding-Modell und LLM-Modell Informationen
 */
export default function RAGStatusComponent() {
  const { data: session } = useSession();
  const [status, setStatus] = useState({
    connected: false,
    tenantStats: null,
    lastChecked: null,
    error: null,
    loading: true
  });

  useEffect(() => {
    const checkStatus = async () => {
      if (!session) return;
      
      try {
        setStatus(prev => ({ ...prev, loading: true }));
        
        const ragClient = new RAGClient();
        const health = await ragClient.checkHealth();
        
        // Wenn wir eine erfolgreiche Antwort erhalten, versuchen wir, die Statistiken abzurufen
        if (health.status === 'ok') {
          try {
            const tenantId = session.user.tenantId;
            const stats = await ragClient.getStats(tenantId);
            
            setStatus({
              connected: true,
              tenantStats: stats,
              lastChecked: new Date(),
              error: null,
              loading: false
            });
          } catch (statsError) {
            // Wenn die Statistik-Abfrage fehlschlägt, sind wir trotzdem verbunden
            setStatus({
              connected: true,
              tenantStats: null,
              lastChecked: new Date(),
              error: `Verbunden, aber Statistik nicht verfügbar: ${statsError.message}`,
              loading: false
            });
          }
        }
      } catch (error) {
        setStatus({
          connected: false,
          tenantStats: null,
          lastChecked: new Date(),
          error: `Verbindung zum RAG-System fehlgeschlagen: ${error.message}`,
          loading: false
        });
      }
    };

    checkStatus();
    
    // Status alle 5 Minuten aktualisieren
    const interval = setInterval(checkStatus, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [session]);

  // Formatierung des Zeitstempels
  const formatDateTime = (date) => {
    if (!date) return 'Nie';
    return new Intl.DateTimeFormat('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          RAG-System-Status
          {status.connected ? (
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              <CheckCircle className="h-3.5 w-3.5 mr-1" />
              Verbunden
            </Badge>
          ) : (
            <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
              <AlertCircle className="h-3.5 w-3.5 mr-1" />
              Nicht verbunden
            </Badge>
          )}
        </CardTitle>
        <CardDescription>
          Aktuelle Informationen über den Status des Retrieval Augmented Generation Systems
        </CardDescription>
      </CardHeader>
      <CardContent>
        {status.loading ? (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-500">Status wird abgerufen...</p>
          </div>
        ) : (
          <div className="space-y-4">
            {status.error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
                {status.error}
              </div>
            )}
            
            {status.connected && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-3 rounded-md">
                    <div className="text-sm font-medium text-gray-500">Zuletzt aktualisiert</div>
                    <div className="mt-1">{formatDateTime(status.lastChecked)}</div>
                  </div>
                  
                  {status.tenantStats && (
                    <div className="bg-gray-50 p-3 rounded-md">
                      <div className="text-sm font-medium text-gray-500">Indexierte Dokumente</div>
                      <div className="mt-1">{status.tenantStats.documentCount || 0}</div>
                    </div>
                  )}
                  
                  {status.tenantStats && status.tenantStats.lastIndexed && (
                    <div className="bg-gray-50 p-3 rounded-md">
                      <div className="text-sm font-medium text-gray-500">Letzte Indexierung</div>
                      <div className="mt-1">{formatDateTime(new Date(status.tenantStats.lastIndexed))}</div>
                    </div>
                  )}
                  
                  {status.tenantStats && (
                    <div className="bg-gray-50 p-3 rounded-md">
                      <div className="text-sm font-medium text-gray-500">Datenquellen</div>
                      <div className="mt-1">{status.tenantStats.dataSources?.join(', ') || 'Keine'}</div>
                    </div>
                  )}
                </div>
                
                <div className="mt-4 text-sm text-gray-500">
                  <p>Embedding-Modell: <span className="font-medium">BAAI/bge-m3</span></p>
                  <p>LLM-Modell: <span className="font-medium">Mistral Large</span></p>
                </div>
              </>
            )}
            
            {!status.connected && !status.loading && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 text-yellow-800">
                <p className="font-medium">Das RAG-System ist derzeit nicht erreichbar.</p>
                <p className="mt-2 text-sm">
                  Stellen Sie sicher, dass der RAG-API-Server läuft und erreichbar ist. 
                  Überprüfen Sie die Umgebungsvariable NEXT_PUBLIC_RAG_API_URL und stellen Sie sicher, 
                  dass sie auf die korrekte URL des RAG-API-Servers verweist.
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
