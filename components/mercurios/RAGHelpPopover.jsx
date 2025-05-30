'use client';

import React from 'react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '../ui/popover';
import { Button } from '../ui/button';
import { HelpCircle } from 'lucide-react';

/**
 * RAGHelpPopover
 * 
 * Eine Komponente, die Hilfetexte und Tipps zur Verwendung des RAG-Systems anzeigt.
 * Diese Komponente kann in verschiedenen RAG-bezogenen Komponenten verwendet werden.
 */
export default function RAGHelpPopover({ type = 'general', placement = 'bottom' }) {
  // Verschiedene Hilfetexte basierend auf dem Typ
  const helpTexts = {
    general: {
      title: 'Über RAG',
      content: (
        <>
          <p className="mb-2">
            RAG (Retrieval Augmented Generation) ist ein KI-System, das Ihre Daten durchsucht und präzise Antworten gibt.
          </p>
          <p>
            Im Gegensatz zu herkömmlichen KI-Systemen bezieht RAG Ihre eigenen Unternehmensdaten ein, was zu genaueren und relevanteren Antworten führt.
          </p>
        </>
      )
    },
    
    query: {
      title: 'Wie stelle ich gute Fragen?',
      content: (
        <>
          <p className="mb-2 font-medium">Tipps für effektive Fragen:</p>
          <ul className="list-disc pl-5 space-y-1 text-sm">
            <li>Seien Sie spezifisch (nennen Sie Zeiträume, Kategorien, etc.)</li>
            <li>Eine Frage pro Anfrage stellen</li>
            <li>Wenn die Antwort zu allgemein ist, stellen Sie eine Folgefrage mit mehr Details</li>
            <li>Für Analysen können Sie nach "Vergleiche", "Trends" oder "Zusammenfassungen" fragen</li>
          </ul>
        </>
      )
    },
    
    insights: {
      title: 'Über Business Insights',
      content: (
        <>
          <p className="mb-2">
            Business Insights werden automatisch aus Ihren Daten generiert und bieten wichtige Erkenntnisse ohne manuelle Abfragen.
          </p>
          <p className="text-sm">
            Die Insights werden regelmäßig aktualisiert und basieren auf aktuellen Geschäftsdaten, Trends und Anomalien in Ihren Daten.
          </p>
        </>
      )
    },
    
    admin: {
      title: 'Datenindexierung',
      content: (
        <>
          <p className="mb-2">
            Die Indexierung ist der Prozess, bei dem Ihre Unternehmensdaten für das RAG-System zugänglich gemacht werden.
          </p>
          <p className="text-sm mb-2">
            <strong>Reguläre Indexierung:</strong> Aktualisiert den Index mit neuen Daten.
          </p>
          <p className="text-sm">
            <strong>Vollständige Neuindexierung:</strong> Erstellt den Index von Grund auf neu. Dies kann bei Datenänderungen oder Problemen hilfreich sein.
          </p>
        </>
      )
    }
  };
  
  const selectedHelp = helpTexts[type] || helpTexts.general;
  
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
          <HelpCircle className="h-4 w-4 text-muted-foreground" />
          <span className="sr-only">Hilfe</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent 
        side={placement} 
        className="w-80 p-4"
        sideOffset={5}
      >
        <div className="space-y-2">
          <h3 className="font-medium">{selectedHelp.title}</h3>
          <div className="text-sm text-muted-foreground">
            {selectedHelp.content}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
