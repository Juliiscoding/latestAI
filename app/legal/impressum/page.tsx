"use client"
import React, { useEffect } from 'react'
import { useLanguage } from '@/components/footer'

export default function ImpressumPage() {
  const { language } = useLanguage();
  
  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl relative z-10">
      <h1 className="text-3xl font-bold mb-8 text-white">
        {language === 'de' ? 'Impressum' : 'Legal Notice'}
      </h1>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Angaben gemäß § 5 TMG</h2>
        <p className="mb-4 text-white/90">
          Mercurios.ai GmbH<br />
          Musterstraße 123<br />
          10115 Berlin<br />
          Deutschland
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Vertreten durch</h3>
        <p className="mb-4 text-white/90">
          Max Mustermann, Geschäftsführer
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Kontakt</h3>
        <p className="mb-4 text-white/90">
          Telefon: +49 (0) 30 123456789<br />
          E-Mail: info@mercurios.ai
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Registereintrag</h3>
        <p className="mb-4 text-white/90">
          Eintragung im Handelsregister.<br />
          Registergericht: Amtsgericht Berlin-Charlottenburg<br />
          Registernummer: HRB 123456
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Umsatzsteuer-ID</h3>
        <p className="mb-4 text-white/90">
          Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:<br />
          DE123456789
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2>
        <p className="mb-4 text-white/90">
          Max Mustermann<br />
          Musterstraße 123<br />
          10115 Berlin<br />
          Deutschland
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Streitschlichtung</h2>
        <p className="mb-4 text-white/90">
          Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: 
          <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer" className="text-[#6ACBDF] hover:underline">
            https://ec.europa.eu/consumers/odr/
          </a>.<br />
          Unsere E-Mail-Adresse finden Sie oben im Impressum.
        </p>
        
        <p className="mb-4 text-white/90">
          Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Haftung für Inhalte</h3>
        <p className="mb-4 text-white/90">
          Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. 
          Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu 
          überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.
        </p>
        
        <p className="text-white/90">
          Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. 
          Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden 
          von entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.
        </p>
      </div>
    </div>
  )
}
