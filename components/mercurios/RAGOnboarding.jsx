'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { CheckCircle, MessageSquare, LightbulbIcon, BarChart3 } from 'lucide-react';

/**
 * RAGOnboarding
 * 
 * Eine Step-by-Step Einführung für neue Benutzer des RAG-Systems.
 * Wird beim ersten Besuch der RAG-Intelligence-Seite angezeigt.
 */
export default function RAGOnboarding() {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  // Beim ersten Rendern prüfen, ob das Onboarding bereits abgeschlossen wurde
  useEffect(() => {
    const onboardingComplete = localStorage.getItem('ragOnboardingComplete');
    if (!onboardingComplete) {
      // Kurze Verzögerung, damit die Seite zuerst vollständig geladen wird
      const timer = setTimeout(() => {
        setOpen(true);
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, []);

  // Onboarding abschließen und Dialog schließen
  const completeOnboarding = () => {
    localStorage.setItem('ragOnboardingComplete', 'true');
    setOpen(false);
  };

  // Zum nächsten Schritt gehen
  const nextStep = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    } else {
      completeOnboarding();
    }
  };

  // Zum vorherigen Schritt zurückgehen
  const prevStep = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  // Onboarding überspringen
  const skipOnboarding = () => {
    completeOnboarding();
  };

  // Inhalte für jeden Schritt
  const steps = [
    {
      title: 'Willkommen zum RAG-Intelligence-System',
      description: 'Entdecken Sie die Kraft der Retrieval Augmented Generation (RAG) für Ihre Geschäftsdaten. In den nächsten Schritten erfahren Sie, wie Sie mit diesem System arbeiten können.',
      icon: <CheckCircle className="h-8 w-8 text-green-500" />,
    },
    {
      title: 'Stellen Sie natürliche Fragen',
      description: 'Im Bereich "Daten abfragen" können Sie Fragen in natürlicher Sprache stellen, wie "Wie haben sich unsere Verkaufszahlen im letzten Quartal entwickelt?" oder "Welche Produkte haben die höchste Gewinnmarge?"',
      icon: <MessageSquare className="h-8 w-8 text-blue-500" />,
    },
    {
      title: 'Entdecken Sie automatische Insights',
      description: 'Im Tab "Business Insights" finden Sie automatisch generierte Erkenntnisse aus Ihren Daten. Diese werden regelmäßig aktualisiert und helfen Ihnen, wichtige Trends und Muster zu erkennen.',
      icon: <LightbulbIcon className="h-8 w-8 text-yellow-500" />,
    },
    {
      title: 'Verstehen Sie Ihre Daten besser',
      description: 'Die RAG-Technologie verbindet Ihre Geschäftsdaten mit fortschrittlicher KI, um tiefere Einblicke zu gewinnen. Alle Antworten basieren auf Ihren eigenen Daten und werden mit Quellen belegt.',
      icon: <BarChart3 className="h-8 w-8 text-purple-500" />,
    },
  ];

  const currentStep = steps[step - 1];

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
            {currentStep.icon}
          </div>
          <DialogTitle className="text-center text-xl">
            {currentStep.title}
          </DialogTitle>
          <DialogDescription className="text-center pt-2">
            {currentStep.description}
          </DialogDescription>
        </DialogHeader>
        
        <div className="flex justify-center py-2">
          {Array.from({ length: totalSteps }, (_, i) => (
            <div
              key={i}
              className={`mx-1 h-2 w-2 rounded-full ${
                i + 1 === step ? 'bg-primary' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
        
        <DialogFooter className="flex flex-col-reverse sm:flex-row sm:justify-between sm:space-x-2">
          <div className="flex flex-row justify-between w-full mt-2 sm:mt-0">
            <Button
              type="button"
              variant="ghost"
              onClick={skipOnboarding}
              className="text-gray-500"
            >
              Überspringen
            </Button>
            
            <div className="flex space-x-2">
              {step > 1 && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={prevStep}
                >
                  Zurück
                </Button>
              )}
              
              <Button type="button" onClick={nextStep}>
                {step === totalSteps ? 'Fertig' : 'Weiter'}
              </Button>
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
