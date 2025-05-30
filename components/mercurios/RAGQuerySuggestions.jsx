'use client';

import React from 'react';
import { Button } from '../ui/button';
import { ScrollArea } from '../ui/scroll-area';

/**
 * RAGQuerySuggestions
 * 
 * Komponente, die dem Benutzer Vorschläge für Fragen an das RAG-System anbietet.
 * Diese können direkt angeklickt werden, um die Frage zu stellen.
 */
export default function RAGQuerySuggestions({ onSelectQuery }) {
  // Kategorisierte Abfragevorschläge
  const suggestions = {
    'Verkauf & Umsatz': [
      'Wie haben sich unsere Verkaufszahlen im letzten Monat entwickelt?',
      'Welche Produkte haben den höchsten Umsatz in diesem Jahr generiert?',
      'Vergleiche den Umsatz des aktuellen Quartals mit dem Vorjahresquartal',
      'Zeige mir die Top 5 Verkaufsregionen nach Umsatz',
      'Wie entwickelte sich der durchschnittliche Bestellwert in den letzten 6 Monaten?'
    ],
    'Produkte & Inventar': [
      'Welche Produkte haben die höchste Gewinnmarge?',
      'Welche Produkte haben die höchste Lagerumschlagsrate?',
      'Gibt es Produkte, die in den nächsten 30 Tagen nachbestellt werden müssen?',
      'Zeige mir Produkte mit niedrigen Lagerbeständen und hoher Nachfrage',
      'Welche Produktkategorien wachsen am schnellsten?'
    ],
    'Kunden & Segmentierung': [
      'Wer sind unsere Top 10 Kunden nach Gesamtumsatz?',
      'Welche Kundensegmente haben die höchste Rentabilität?',
      'Wie hat sich die Kundenbindung im Vergleich zum Vorjahr entwickelt?',
      'Identifiziere Kunden mit hohem Abwanderungsrisiko',
      'Welche Kunden haben im letzten Quartal mehr gekauft als im Vorquartal?'
    ],
    'Geschäftstrends & Prognosen': [
      'Was sind die wichtigsten Geschäftstrends der letzten 3 Monate?',
      'Erstelle eine Umsatzprognose für das nächste Quartal',
      'Welche saisonalen Muster zeigen unsere Verkaufsdaten?',
      'Gibt es ungewöhnliche Abweichungen in unseren aktuellen Verkaufszahlen?',
      'Wie könnten sich die aktuellen Marktbedingungen auf unser Geschäft auswirken?'
    ]
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 mt-4 border border-gray-100">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Beispielfragen, die Sie stellen können:</h3>
      
      <ScrollArea className="h-60 pr-4">
        <div className="space-y-4">
          {Object.entries(suggestions).map(([category, queries]) => (
            <div key={category}>
              <h4 className="text-xs font-medium text-gray-500 mb-2">{category}</h4>
              <div className="flex flex-wrap gap-2">
                {queries.map((query, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="text-xs bg-white hover:bg-blue-50 text-gray-700 hover:text-blue-700"
                    onClick={() => onSelectQuery(query)}
                  >
                    {query.length > 40 ? `${query.substring(0, 40)}...` : query}
                  </Button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
