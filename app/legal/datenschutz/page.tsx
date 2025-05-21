"use client"
import React from 'react'
import { useLanguage } from '@/components/language-provider'

export default function DatenschutzPage() {
  const { language } = useLanguage();
  
  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl relative z-10">
      <h1 className="text-3xl font-bold mb-8 text-white">
        {language === 'de' ? 'Datenschutzerklärung' : 'Privacy Policy'}
      </h1>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">1. Datenschutz auf einen Blick</h2>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Allgemeine Hinweise</h3>
        <p className="mb-4 text-white/90">
          Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen Daten passiert, 
          wenn Sie diese Website besuchen. Personenbezogene Daten sind alle Daten, mit denen Sie persönlich identifiziert 
          werden können. Ausführliche Informationen zum Thema Datenschutz entnehmen Sie unserer unter diesem Text 
          aufgeführten Datenschutzerklärung.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Datenerfassung auf dieser Website</h3>
        <p className="mb-4 text-white/90">
          <strong>Wer ist verantwortlich für die Datenerfassung auf dieser Website?</strong><br />
          Die Datenverarbeitung auf dieser Website erfolgt durch den Websitebetreiber. Dessen Kontaktdaten 
          können Sie dem Impressum dieser Website entnehmen.
        </p>
        
        <p className="mb-4 text-white/90">
          <strong>Wie erfassen wir Ihre Daten?</strong><br />
          Ihre Daten werden zum einen dadurch erhoben, dass Sie uns diese mitteilen. Hierbei kann es sich z. B. um Daten handeln, 
          die Sie in ein Kontaktformular eingeben.
        </p>
        
        <p className="mb-4 text-white/90">
          Andere Daten werden automatisch oder nach Ihrer Einwilligung beim Besuch der Website durch unsere IT-Systeme erfasst. 
          Das sind vor allem technische Daten (z. B. Internetbrowser, Betriebssystem oder Uhrzeit des Seitenaufrufs). 
          Die Erfassung dieser Daten erfolgt automatisch, sobald Sie diese Website betreten.
        </p>
        
        <p className="mb-4 text-white/90">
          <strong>Wofür nutzen wir Ihre Daten?</strong><br />
          Ein Teil der Daten wird erhoben, um eine fehlerfreie Bereitstellung der Website zu gewährleisten. 
          Andere Daten können zur Analyse Ihres Nutzerverhaltens verwendet werden.
        </p>
        
        <p className="mb-4 text-white/90">
          <strong>Welche Rechte haben Sie bezüglich Ihrer Daten?</strong><br />
          Sie haben jederzeit das Recht, unentgeltlich Auskunft über Herkunft, Empfänger und Zweck Ihrer gespeicherten 
          personenbezogenen Daten zu erhalten. Sie haben außerdem ein Recht, die Berichtigung oder Löschung dieser Daten zu verlangen. 
          Wenn Sie eine Einwilligung zur Datenverarbeitung erteilt haben, können Sie diese Einwilligung jederzeit für die Zukunft widerrufen. 
          Außerdem haben Sie das Recht, unter bestimmten Umständen die Einschränkung der Verarbeitung Ihrer personenbezogenen Daten zu verlangen.
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">2. Allgemeine Hinweise und Pflichtinformationen</h2>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Datenschutz</h3>
        <p className="mb-4 text-white/90">
          Die Betreiber dieser Seiten nehmen den Schutz Ihrer persönlichen Daten sehr ernst. Wir behandeln Ihre personenbezogenen Daten 
          vertraulich und entsprechend der gesetzlichen Datenschutzvorschriften sowie dieser Datenschutzerklärung.
        </p>
        
        <p className="mb-4 text-white/90">
          Wenn Sie diese Website benutzen, werden verschiedene personenbezogene Daten erhoben. Personenbezogene Daten sind Daten, 
          mit denen Sie persönlich identifiziert werden können. Die vorliegende Datenschutzerklärung erläutert, welche Daten wir erheben 
          und wofür wir sie nutzen. Sie erläutert auch, wie und zu welchem Zweck das geschieht.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Hinweis zur verantwortlichen Stelle</h3>
        <p className="mb-4 text-white/90">
          Die verantwortliche Stelle für die Datenverarbeitung auf dieser Website ist:<br /><br />
          
          Mercurios.ai GmbH<br />
          Musterstraße 123<br />
          10115 Berlin<br />
          Deutschland<br /><br />
          
          Telefon: +49 (0) 30 123456789<br />
          E-Mail: info@mercurios.ai
        </p>
        
        <p className="mb-4 text-white/90">
          Verantwortliche Stelle ist die natürliche oder juristische Person, die allein oder gemeinsam mit anderen über die Zwecke und 
          Mittel der Verarbeitung von personenbezogenen Daten (z. B. Namen, E-Mail-Adressen o. Ä.) entscheidet.
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">3. Datenerfassung auf dieser Website</h2>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Cookies</h3>
        <p className="mb-4 text-white/90">
          Unsere Internetseiten verwenden so genannte „Cookies". Cookies sind kleine Textdateien und richten auf Ihrem Endgerät keinen Schaden an. 
          Sie werden entweder vorübergehend für die Dauer einer Sitzung (Session-Cookies) oder dauerhaft (permanente Cookies) auf Ihrem Endgerät gespeichert. 
          Session-Cookies werden nach Ende Ihres Besuchs automatisch gelöscht. Permanente Cookies bleiben auf Ihrem Endgerät gespeichert, bis Sie diese selbst 
          löschen oder eine automatische Löschung durch Ihren Webbrowser erfolgt.
        </p>
        
        <p className="mb-4 text-white/90">
          Cookies können von uns (First-Party-Cookies) oder von Drittunternehmen stammen (sog. Third-Party-Cookies). 
          Third-Party-Cookies ermöglichen die Einbindung bestimmter Dienstleistungen von Drittunternehmen innerhalb von Webseiten 
          (z. B. Cookies zur Abwicklung von Zahlungsdienstleistungen).
        </p>
        
        <p className="mb-4 text-white/90">
          Cookies haben verschiedene Funktionen. Zahlreiche Cookies sind technisch notwendig, da bestimmte Websitefunktionen ohne diese nicht 
          funktionieren würden (z. B. die Warenkorbfunktion oder die Anzeige von Videos). Andere Cookies dienen dazu, das Nutzerverhalten 
          auszuwerten oder Werbung anzuzeigen.
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">4. Ihre Rechte als betroffene Person</h2>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Recht auf Auskunft</h3>
        <p className="mb-4 text-white/90">
          Sie haben das Recht, jederzeit unentgeltlich Auskunft über die zu Ihrer Person gespeicherten personenbezogenen Daten, 
          deren Herkunft und Empfänger und den Zweck der Datenverarbeitung zu erhalten.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Recht auf Berichtigung</h3>
        <p className="mb-4 text-white/90">
          Sie haben das Recht, die Berichtigung Ihrer unrichtigen personenbezogenen Daten zu verlangen. 
          Ferner steht Ihnen das Recht zu, unter Berücksichtigung der Zwecke der Verarbeitung, die Vervollständigung 
          unvollständiger personenbezogener Daten zu verlangen.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Recht auf Löschung („Recht auf Vergessenwerden")</h3>
        <p className="mb-4 text-white/90">
          Sie haben das Recht, von uns zu verlangen, dass die Sie betreffenden personenbezogenen Daten unverzüglich gelöscht werden, 
          sofern einer der gesetzlich vorgesehenen Gründe zutrifft und soweit die Verarbeitung nicht erforderlich ist.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Recht auf Einschränkung der Verarbeitung</h3>
        <p className="mb-4 text-white/90">
          Sie haben das Recht, von uns die Einschränkung der Verarbeitung zu verlangen, wenn eine der gesetzlichen Voraussetzungen gegeben ist.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Recht auf Datenübertragbarkeit</h3>
        <p className="mb-4 text-white/90">
          Sie haben das Recht, die Sie betreffenden personenbezogenen Daten, die Sie uns bereitgestellt haben, in einem strukturierten, 
          gängigen und maschinenlesbaren Format zu erhalten. Außerdem haben Sie das Recht, diese Daten einem anderen Verantwortlichen ohne 
          Behinderung durch uns zu übermitteln, sofern die Verarbeitung auf einer Einwilligung oder auf einem Vertrag beruht und die Verarbeitung 
          bei uns mithilfe automatisierter Verfahren erfolgt.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Widerspruchsrecht</h3>
        <p className="text-white/90">
          Sie haben das Recht, aus Gründen, die sich aus Ihrer besonderen Situation ergeben, jederzeit gegen die Verarbeitung Sie betreffender 
          personenbezogener Daten Widerspruch einzulegen.
        </p>
      </div>
    </div>
  )
}
