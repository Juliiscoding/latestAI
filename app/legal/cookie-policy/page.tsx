"use client"
import React from 'react'
import { useLanguage } from '@/components/language-provider'

export default function CookiePolicyPage() {
  const { language } = useLanguage();
  
  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl relative z-10">
      <h1 className="text-3xl font-bold mb-8 text-white">
        {language === 'de' ? 'Cookie-Richtlinie' : 'Cookie Policy'}
      </h1>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">1. Was sind Cookies?</h2>
        <p className="mb-4 text-white/90">
          Cookies sind kleine Textdateien, die auf Ihrem Computer oder mobilen Gerät gespeichert werden, wenn Sie unsere Website besuchen. 
          Sie ermöglichen es uns, Ihren Browser beim nächsten Besuch wiederzuerkennen und bieten Ihnen ein verbessertes Nutzererlebnis.
        </p>
        
        <p className="mb-4 text-white/90">
          Cookies können entweder von uns (First-Party-Cookies) oder von Drittanbietern (Third-Party-Cookies) stammen, 
          die mit unserer Erlaubnis Cookies auf unserer Website platzieren.
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">2. Arten von Cookies, die wir verwenden</h2>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Unbedingt erforderliche Cookies</h3>
        <p className="mb-4 text-white/90">
          Diese Cookies sind für das Funktionieren unserer Website unerlässlich und können in unseren Systemen nicht abgeschaltet werden. 
          Sie werden in der Regel nur als Reaktion auf von Ihnen getätigte Aktionen gesetzt, die einer Dienstanforderung entsprechen, 
          wie etwa dem Festlegen Ihrer Datenschutzeinstellungen, dem Anmelden oder dem Ausfüllen von Formularen.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Funktionale Cookies</h3>
        <p className="mb-4 text-white/90">
          Diese Cookies ermöglichen es uns, erweiterte Funktionalitäten und Personalisierung bereitzustellen, wie z.B. Videos und Live-Chats. 
          Sie können von uns oder von Drittanbietern gesetzt werden, deren Dienste wir auf unseren Seiten eingebunden haben.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Analytische Cookies</h3>
        <p className="mb-4 text-white/90">
          Diese Cookies ermöglichen es uns, Besuche und Verkehrsquellen zu zählen, damit wir die Leistung unserer Website messen und verbessern können. 
          Sie helfen uns zu verstehen, welche Seiten am beliebtesten und welche am wenigsten beliebt sind, und zu sehen, wie sich Besucher auf der 
          Website bewegen.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Marketing-Cookies</h3>
        <p className="mb-4 text-white/90">
          Diese Cookies können von unseren Werbepartnern über unsere Website gesetzt werden. Sie können von diesen Unternehmen verwendet werden, 
          um ein Profil Ihrer Interessen zu erstellen und Ihnen relevante Werbung auf anderen Websites zu zeigen.
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">3. Wie Sie Cookies kontrollieren können</h2>
        <p className="mb-4 text-white/90">
          Sie können Ihre Cookie-Einstellungen jederzeit anpassen, indem Sie auf die Schaltfläche "Cookie-Einstellungen" am unteren Rand 
          unserer Website klicken. Darüber hinaus können Sie Cookies über die Einstellungen Ihres Browsers verwalten.
        </p>
        
        <p className="mb-4 text-white/90">
          Bitte beachten Sie, dass das Blockieren einiger Arten von Cookies die Funktionalität unserer Website und die Dienste, 
          die wir anbieten können, beeinträchtigen kann.
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">4. Cookies von Drittanbietern</h2>
        <p className="mb-4 text-white/90">
          Wir verwenden Dienste von Drittanbietern, die möglicherweise Cookies auf Ihrem Gerät setzen. Nachfolgend finden Sie Informationen 
          zu diesen Drittanbietern und den von ihnen verwendeten Cookies:
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Google Analytics</h3>
        <p className="mb-4 text-white/90">
          Wir verwenden Google Analytics, um zu verstehen, wie Besucher mit unserer Website interagieren. 
          Google Analytics verwendet Cookies, um Informationen über Ihre Nutzung unserer Website zu sammeln.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Google Ads</h3>
        <p className="mb-4 text-white/90">
          Wir verwenden Google Ads, um Werbung zu schalten. Google Ads verwendet Cookies, um relevantere Anzeigen zu schalten 
          und die Leistung von Werbekampagnen zu messen.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Facebook Pixel</h3>
        <p className="mb-4 text-white/90">
          Wir verwenden Facebook Pixel, um die Wirksamkeit unserer Werbung auf Facebook zu messen und zu verstehen, 
          welche Aktionen Sie auf unserer Website ausführen.
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">5. Änderungen an unserer Cookie-Richtlinie</h2>
        <p className="mb-4 text-white/90">
          Wir behalten uns das Recht vor, diese Cookie-Richtlinie jederzeit zu ändern. Änderungen werden auf dieser Seite veröffentlicht. 
          Bitte überprüfen Sie diese Seite regelmäßig, um über Änderungen informiert zu bleiben.
        </p>
        
        <h2 className="text-xl font-semibold my-4 text-[#6ACBDF]">6. Kontakt</h2>
        <p className="text-white/90">
          Wenn Sie Fragen zu unserer Cookie-Richtlinie haben, kontaktieren Sie uns bitte unter:<br />
          E-Mail: datenschutz@mercurios.ai<br />
          Telefon: +49 (0) 30 123456789
        </p>
      </div>
    </div>
  )
}
