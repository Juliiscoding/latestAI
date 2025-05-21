"use client"
import React from 'react'
import { useLanguage } from '@/components/language-provider'

export default function WiderrufsrechtPage() {
  const { language } = useLanguage();
  
  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl relative z-10">
      <h1 className="text-3xl font-bold mb-8 text-white">
        {language === 'de' ? 'Widerrufsrecht' : 'Right of Withdrawal'}
      </h1>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Widerrufsbelehrung</h2>
        <p className="mb-4 text-white/90">
          Als Verbraucher haben Sie das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Widerrufsfrist</h3>
        <p className="mb-4 text-white/90">
          Die Widerrufsfrist beträgt vierzehn Tage ab dem Tag des Vertragsabschlusses.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Ausübung des Widerrufsrechts</h3>
        <p className="mb-4 text-white/90">
          Um Ihr Widerrufsrecht auszuüben, müssen Sie uns (Mercurios.ai GmbH, Musterstraße 123, 10115 Berlin, Deutschland, 
          Telefon: +49 (0) 30 123456789, E-Mail: widerruf@mercurios.ai) mittels einer eindeutigen Erklärung (z.B. ein mit der Post 
          versandter Brief oder eine E-Mail) über Ihren Entschluss, diesen Vertrag zu widerrufen, informieren. Sie können dafür das 
          beigefügte Muster-Widerrufsformular verwenden, das jedoch nicht vorgeschrieben ist.
        </p>
        
        <p className="mb-4 text-white/90">
          Zur Wahrung der Widerrufsfrist reicht es aus, dass Sie die Mitteilung über die Ausübung des Widerrufsrechts vor Ablauf der 
          Widerrufsfrist absenden.
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Folgen des Widerrufs</h2>
        <p className="mb-4 text-white/90">
          Wenn Sie diesen Vertrag widerrufen, haben wir Ihnen alle Zahlungen, die wir von Ihnen erhalten haben, einschließlich der 
          Lieferkosten (mit Ausnahme der zusätzlichen Kosten, die sich daraus ergeben, dass Sie eine andere Art der Lieferung als die 
          von uns angebotene, günstigste Standardlieferung gewählt haben), unverzüglich und spätestens binnen vierzehn Tagen ab dem Tag 
          zurückzuzahlen, an dem die Mitteilung über Ihren Widerruf dieses Vertrags bei uns eingegangen ist. Für diese Rückzahlung 
          verwenden wir dasselbe Zahlungsmittel, das Sie bei der ursprünglichen Transaktion eingesetzt haben, es sei denn, mit Ihnen 
          wurde ausdrücklich etwas anderes vereinbart; in keinem Fall werden Ihnen wegen dieser Rückzahlung Entgelte berechnet.
        </p>
        
        <p className="mb-4 text-white/90">
          Haben Sie verlangt, dass die Dienstleistungen während der Widerrufsfrist beginnen sollen, so haben Sie uns einen angemessenen 
          Betrag zu zahlen, der dem Anteil der bis zu dem Zeitpunkt, zu dem Sie uns von der Ausübung des Widerrufsrechts hinsichtlich 
          dieses Vertrags unterrichten, bereits erbrachten Dienstleistungen im Vergleich zum Gesamtumfang der im Vertrag vorgesehenen 
          Dienstleistungen entspricht.
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Muster-Widerrufsformular</h2>
        <p className="mb-4 text-white/90">
          (Wenn Sie den Vertrag widerrufen wollen, dann füllen Sie bitte dieses Formular aus und senden Sie es zurück.)
        </p>
        
        <div className="border border-white/20 rounded p-4 mb-4 text-white/90">
          <p className="mb-2">An:</p>
          <p className="mb-2">
            Mercurios.ai GmbH<br />
            Musterstraße 123<br />
            10115 Berlin<br />
            Deutschland<br />
            E-Mail: widerruf@mercurios.ai
          </p>
          <p className="mb-2">
            Hiermit widerrufe(n) ich/wir (*) den von mir/uns (*) abgeschlossenen Vertrag über den Kauf der folgenden Waren (*)/die 
            Erbringung der folgenden Dienstleistung (*)
          </p>
          <p className="mb-2">Bestellt am (*)/erhalten am (*)</p>
          <p className="mb-2">Name des/der Verbraucher(s)</p>
          <p className="mb-2">Anschrift des/der Verbraucher(s)</p>
          <p className="mb-2">Unterschrift des/der Verbraucher(s) (nur bei Mitteilung auf Papier)</p>
          <p>Datum</p>
        </div>
        
        <p className="text-white/70 text-sm italic">
          (*) Unzutreffendes streichen.
        </p>
      </div>
    </div>
  )
}
