'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { ArrowRight, HelpCircle, Lightbulb, Search, BookOpen } from 'lucide-react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '../ui/accordion';

/**
 * RAGIntroductionComponent
 * 
 * Eine Komponente, die neuen Benutzern eine Einführung in das RAG-System gibt
 * und Tipps zur effektiven Nutzung bereitstellt.
 */
export default function RAGIntroductionComponent() {
  const [showIntro, setShowIntro] = useState(true);
  const [hasDismissedBefore, setHasDismissedBefore] = useState(false);

  // Beim ersten Rendern prüfen, ob die Einführung bereits geschlossen wurde
  useEffect(() => {
    const introDismissed = localStorage.getItem('ragIntroDismissed');
    if (introDismissed) {
      setHasDismissedBefore(true);
      setShowIntro(false);
    }
  }, []);

  // Einführung ausblenden und diese Entscheidung speichern
  const handleDismiss = (permanent = false) => {
    setShowIntro(false);
    if (permanent) {
      localStorage.setItem('ragIntroDismissed', 'true');
      setHasDismissedBefore(true);
    }
  };

  // Einführung wieder anzeigen
  const handleShowIntro = () => {
    setShowIntro(true);
  };

  if (!showIntro) {
    if (hasDismissedBefore) {
      return null; // Komplett ausblenden, wenn dauerhaft geschlossen
    }
    
    // Minimierte Version anzeigen, wenn temporär geschlossen
    return (
      <div className="mb-4 flex justify-end">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleShowIntro}
          className="flex items-center gap-2"
        >
          <HelpCircle className="h-4 w-4" />
          <span>Einführung anzeigen</span>
        </Button>
      </div>
    );
  }

  return (
    <Card className="mb-6 border border-blue-100 bg-blue-50">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center">
          <CardTitle className="text-blue-800">
            <BookOpen className="inline-block mr-2 h-5 w-5" />
            Willkommen zum RAG-Intelligence-System
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => handleDismiss(false)}
              className="text-blue-700 hover:text-blue-800 hover:bg-blue-100"
            >
              Ausblenden
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => handleDismiss(true)}
              className="text-blue-700 hover:text-blue-800 hover:bg-blue-100"
            >
              Nicht mehr anzeigen
            </Button>
          </div>
        </div>
        <CardDescription className="text-blue-700">
          Entdecken Sie die Kraft der Retrieval Augmented Generation (RAG) für Ihre Geschäftsdaten
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="text-blue-700">
            <p>
              Das RAG-Intelligence-System ermöglicht es Ihnen, Ihre Geschäftsdaten durch natürliche Sprache abzufragen und 
              automatisch generierte Erkenntnisse zu entdecken. Hier sind einige Tipps, um das Beste aus dem System herauszuholen:
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div className="bg-white p-4 rounded-lg shadow-sm border border-blue-100">
              <div className="flex items-start">
                <div className="mr-3 mt-1">
                  <Search className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-blue-800">Stellen Sie präzise Fragen</h3>
                  <p className="text-sm mt-1 text-blue-700">
                    Je spezifischer Ihre Fragen sind, desto genauer werden die Antworten sein. 
                    Fügen Sie relevante Details wie Zeiträume oder Produktkategorien hinzu.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-sm border border-blue-100">
              <div className="flex items-start">
                <div className="mr-3 mt-1">
                  <Lightbulb className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-blue-800">Nutzen Sie automatische Insights</h3>
                  <p className="text-sm mt-1 text-blue-700">
                    Das System generiert automatisch Business Insights basierend auf Ihren Daten.
                    Überprüfen Sie den Insights-Tab regelmäßig auf neue Erkenntnisse.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="example-questions" className="border-blue-200">
              <AccordionTrigger className="text-blue-800 hover:text-blue-900 hover:no-underline py-2">
                Beispielfragen, die Sie stellen können
              </AccordionTrigger>
              <AccordionContent className="text-blue-700">
                <ul className="space-y-2 list-disc pl-5">
                  <li>Wie haben sich unsere Verkaufszahlen in der letzten Woche entwickelt?</li>
                  <li>Welche Produkte haben die höchste Gewinnmarge?</li>
                  <li>Fasse die wichtigsten Kennzahlen für [Produktkategorie] im letzten Quartal zusammen.</li>
                  <li>Wer sind unsere Top 5 Kunden nach Umsatz?</li>
                  <li>Vergleiche die Leistung verschiedener Vertriebskanäle.</li>
                </ul>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="how-it-works" className="border-blue-200">
              <AccordionTrigger className="text-blue-800 hover:text-blue-900 hover:no-underline py-2">
                Wie funktioniert RAG?
              </AccordionTrigger>
              <AccordionContent className="text-blue-700">
                <p className="mb-2">
                  RAG (Retrieval Augmented Generation) kombiniert zwei leistungsstarke KI-Technologien:
                </p>
                <ol className="list-decimal pl-5 space-y-1">
                  <li><strong>Retrieval:</strong> Das System durchsucht Ihre indexierten Daten, um relevante Informationen zu finden.</li>
                  <li><strong>Generation:</strong> Eine KI verwendet diese Informationen, um präzise und kontextbezogene Antworten zu generieren.</li>
                </ol>
                <p className="mt-2">
                  Dieser Ansatz ermöglicht es dem System, auf Ihre spezifischen Geschäftsdaten zu reagieren und nicht nur auf allgemeines 
                  Wissen zurückzugreifen.
                </p>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
          
          <div className="mt-4 flex justify-end">
            <Button 
              onClick={() => handleDismiss(false)} 
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
            >
              <span>Jetzt loslegen</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
