import React from 'react'

export default function ContactPage() {
  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8 text-white">Kontakt</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Kontaktieren Sie uns</h2>
          <p className="mb-6 text-white/90">
            Haben Sie Fragen zu unseren Produkten oder Dienstleistungen? Wir freuen uns, von Ihnen zu hören!
            Füllen Sie einfach das Formular aus, und wir werden uns so schnell wie möglich bei Ihnen melden.
          </p>
          
          <form className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-white mb-1">Name</label>
              <input
                type="text"
                id="name"
                className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-[#6ACBDF] focus:border-transparent"
                placeholder="Ihr Name"
              />
            </div>
            
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-white mb-1">E-Mail</label>
              <input
                type="email"
                id="email"
                className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-[#6ACBDF] focus:border-transparent"
                placeholder="ihre.email@beispiel.de"
              />
            </div>
            
            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-white mb-1">Betreff</label>
              <input
                type="text"
                id="subject"
                className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-[#6ACBDF] focus:border-transparent"
                placeholder="Betreff Ihrer Nachricht"
              />
            </div>
            
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-white mb-1">Nachricht</label>
              <textarea
                id="message"
                rows={5}
                className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-[#6ACBDF] focus:border-transparent"
                placeholder="Ihre Nachricht an uns..."
              />
            </div>
            
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="h-4 w-4 text-[#6ACBDF] focus:ring-[#6ACBDF] border-white/20 rounded"
                />
                <span className="ml-2 text-sm text-white/90">
                  Ich habe die <a href="/legal/datenschutz" className="text-[#6ACBDF] hover:underline">Datenschutzerklärung</a> gelesen und stimme zu.
                </span>
              </label>
            </div>
            
            <button
              type="submit"
              className="px-4 py-2 bg-[#6ACBDF] text-black font-medium rounded-md hover:bg-[#6ACBDF]/80 transition-colors"
            >
              Nachricht senden
            </button>
          </form>
        </div>
        
        <div>
          <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Kontaktdaten</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-white mb-1">Adresse</h3>
                <p className="text-white/90">
                  Mercurios.ai GmbH<br />
                  Musterstraße 123<br />
                  10115 Berlin<br />
                  Deutschland
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-white mb-1">Telefon</h3>
                <p className="text-white/90">+49 (0) 30 123456789</p>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-white mb-1">E-Mail</h3>
                <p className="text-white/90">info@mercurios.ai</p>
              </div>
            </div>
          </div>
          
          <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Geschäftszeiten</h2>
            <div className="space-y-2 text-white/90">
              <p>Montag - Freitag: 9:00 - 17:00 Uhr</p>
              <p>Samstag & Sonntag: Geschlossen</p>
              <p className="mt-4 text-white/70">
                An gesetzlichen Feiertagen geschlossen.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
