'use client';

import React from 'react';
import { AlertTriangle, AlertCircle, HelpCircle, RefreshCw } from 'lucide-react';
import { Button } from '../ui/button';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';

/**
 * RAGErrorHandling
 * 
 * Komponente zur benutzerfreundlichen Darstellung von Fehlern beim RAG-System
 * mit konkreten Lösungsvorschlägen und Hilfestellungen.
 */
export default function RAGErrorHandling({ 
  error, 
  variant = 'default',
  onRetry = null,
  className = ''
}) {
  // Funktion, um freundliche Fehlermeldungen basierend auf dem Fehlertyp zu generieren
  const getFriendlyErrorMessage = (errorObj) => {
    if (!errorObj) return null;
    
    // Standardnachricht, falls keine spezifischere Nachricht gefunden wird
    let message = {
      title: 'Ein Fehler ist aufgetreten',
      description: 'Beim Zugriff auf das RAG-System ist ein unerwarteter Fehler aufgetreten.',
      solution: 'Bitte versuchen Sie es später erneut oder kontaktieren Sie den Support.'
    };
    
    const errorMessage = typeof errorObj === 'string' ? errorObj : errorObj.message || JSON.stringify(errorObj);
    
    // Spezifische Fehlermeldungen basierend auf erkannten Mustern
    if (errorMessage.includes('not responding') || errorMessage.includes('timeout') || errorMessage.includes('ECONNREFUSED')) {
      message = {
        title: 'Verbindungsproblem',
        description: 'Das RAG-System ist derzeit nicht erreichbar.',
        solution: 'Bitte überprüfen Sie Ihre Internetverbindung und stellen Sie sicher, dass der RAG-Server aktiv ist.'
      };
    } else if (errorMessage.includes('401') || errorMessage.includes('unauthorized') || errorMessage.includes('not authenticated')) {
      message = {
        title: 'Authentifizierungsproblem',
        description: 'Sie sind nicht autorisiert, auf das RAG-System zuzugreifen.',
        solution: 'Bitte melden Sie sich erneut an oder wenden Sie sich an Ihren Administrator.'
      };
    } else if (errorMessage.includes('403') || errorMessage.includes('forbidden')) {
      message = {
        title: 'Zugriff verweigert',
        description: 'Sie haben keine Berechtigung, diese Aktion auszuführen.',
        solution: 'Wenden Sie sich an Ihren Administrator, um die entsprechenden Berechtigungen zu erhalten.'
      };
    } else if (errorMessage.includes('not indexed') || errorMessage.includes('no data') || errorMessage.includes('empty index')) {
      message = {
        title: 'Keine Daten verfügbar',
        description: 'Es wurden keine indizierten Daten für Ihren Tenant gefunden.',
        solution: 'Bitte kontaktieren Sie Ihren Administrator, um die Datenindexierung zu starten.'
      };
    } else if (errorMessage.includes('rate limit') || errorMessage.includes('too many requests')) {
      message = {
        title: 'Anfragelimit erreicht',
        description: 'Sie haben zu viele Anfragen in kurzer Zeit gestellt.',
        solution: 'Bitte warten Sie einen Moment und versuchen Sie es dann erneut.'
      };
    }
    
    return message;
  };
  
  // Wenn kein Fehler vorliegt, nichts rendern
  if (!error) return null;
  
  const errorInfo = getFriendlyErrorMessage(error);
  
  // Verschiedene Varianten der Fehleranzeige
  const renderAlert = () => {
    return (
      <Alert variant="destructive" className={className}>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>{errorInfo.title}</AlertTitle>
        <AlertDescription>
          <p>{errorInfo.description}</p>
          <p className="mt-2 text-sm">{errorInfo.solution}</p>
          {onRetry && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onRetry} 
              className="mt-2 flex items-center gap-1"
            >
              <RefreshCw className="h-3 w-3" />
              <span>Erneut versuchen</span>
            </Button>
          )}
        </AlertDescription>
      </Alert>
    );
  };
  
  const renderInline = () => {
    return (
      <div className={`p-4 bg-red-50 border border-red-200 rounded-md text-red-700 ${className}`}>
        <div className="flex items-start">
          <AlertTriangle className="h-5 w-5 mt-0.5 mr-2 flex-shrink-0" />
          <div>
            <h4 className="font-medium">{errorInfo.title}</h4>
            <p className="mt-1 text-sm">{errorInfo.description}</p>
            <p className="mt-2 text-sm font-medium">{errorInfo.solution}</p>
            {onRetry && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onRetry} 
                className="mt-2 flex items-center gap-1 bg-white"
              >
                <RefreshCw className="h-3 w-3" />
                <span>Erneut versuchen</span>
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  };
  
  const renderMinimal = () => {
    return (
      <div className={`flex items-center text-red-600 ${className}`}>
        <AlertCircle className="h-4 w-4 mr-2" />
        <span>{errorInfo.title}: {errorInfo.description}</span>
        {onRetry && (
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onRetry} 
            className="ml-2 h-6 px-2 text-red-600 hover:text-red-700 hover:bg-red-50"
          >
            <RefreshCw className="h-3 w-3" />
          </Button>
        )}
      </div>
    );
  };
  
  const renderHelp = () => {
    return (
      <div className={`bg-amber-50 border border-amber-200 rounded-md p-4 ${className}`}>
        <div className="flex items-start">
          <HelpCircle className="h-5 w-5 text-amber-600 mt-0.5 mr-2 flex-shrink-0" />
          <div>
            <h4 className="font-medium text-amber-800">{errorInfo.title}</h4>
            <p className="mt-1 text-sm text-amber-700">{errorInfo.description}</p>
            <div className="mt-3 p-3 bg-white rounded border border-amber-100">
              <h5 className="text-sm font-medium text-amber-800">Lösungsvorschläge:</h5>
              <p className="mt-1 text-sm text-amber-700">{errorInfo.solution}</p>
              
              <div className="mt-2 pt-2 border-t border-amber-100">
                <h5 className="text-sm font-medium text-amber-800">Häufige Probleme:</h5>
                <ul className="mt-1 text-sm text-amber-700 list-disc pl-5 space-y-1">
                  <li>Stellen Sie sicher, dass der RAG-Server läuft</li>
                  <li>Überprüfen Sie Ihre Internetverbindung</li>
                  <li>Melden Sie sich erneut an, um Ihre Sitzung zu aktualisieren</li>
                </ul>
              </div>
            </div>
            
            {onRetry && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onRetry} 
                className="mt-3 flex items-center gap-1 bg-white border-amber-200 text-amber-700 hover:bg-amber-50 hover:text-amber-800"
              >
                <RefreshCw className="h-3 w-3" />
                <span>Erneut versuchen</span>
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  };
  
  // Je nach Variante die entsprechende Darstellung rendern
  switch (variant) {
    case 'inline':
      return renderInline();
    case 'minimal':
      return renderMinimal();
    case 'help':
      return renderHelp();
    case 'alert':
    default:
      return renderAlert();
  }
}
