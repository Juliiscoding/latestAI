"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import Navbar from "@/components/navbar"
import { SplashCursor } from "@/components/ui/splash-cursor"
import { useLanguage } from "@/components/language-provider"

export default function DemoPage() {
  const router = useRouter()
  const { language } = useLanguage()
  const [formData, setFormData] = useState({
    fullName: "",
    companyName: "",
    email: "",
    phoneNumber: "",
    message: "",
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false)
      setIsSubmitted(true)
    }, 1500)
  }

  const texts = {
    title: language === 'de' ? 'Demo buchen' : 'Book a Demo',
    subtitle: language === 'de' 
      ? 'Vereinbaren Sie einen Termin mit unserem Team, um zu sehen, wie Mercurios.ai Ihr Einzelhandelsgeschäft transformieren kann'
      : 'Schedule a session with our team to see how Mercurios.ai can transform your retail business',
    fullName: language === 'de' ? 'Vollständiger Name' : 'Full Name',
    companyName: language === 'de' ? 'Unternehmensname' : 'Company Name',
    email: language === 'de' ? 'E-Mail' : 'Email',
    phoneNumber: language === 'de' ? 'Telefonnummer' : 'Phone Number',
    message: language === 'de' ? 'Nachricht (optional)' : 'Message (optional)',
    messagePlaceholder: language === 'de' 
      ? 'Teilen Sie uns mit, welche spezifischen Herausforderungen Sie haben oder was Sie von der Demo erwarten...'
      : 'Let us know what specific challenges you have or what you expect from the demo...',
    submitButton: language === 'de' ? 'Demo anfordern' : 'Request Demo',
    submitting: language === 'de' ? 'Wird gesendet...' : 'Submitting...',
    successTitle: language === 'de' ? 'Anfrage erhalten!' : 'Request Received!',
    successMessage: language === 'de'
      ? 'Vielen Dank für Ihr Interesse an Mercurios.ai. Unser Team wird sich innerhalb von 24 Stunden mit Ihnen in Verbindung setzen, um einen Demo-Termin zu vereinbaren.'
      : 'Thank you for your interest in Mercurios.ai. Our team will contact you within 24 hours to schedule a demo session.',
    backToHome: language === 'de' ? 'Zurück zur Startseite' : 'Back to Home'
  }

  return (
    <main className="min-h-screen bg-black antialiased relative overflow-hidden">
      {/* Splash cursor background effect */}
      <div className="absolute inset-0 z-0">
        <SplashCursor 
          BACK_COLOR={{ r: 0, g: 0, b: 0 }}
          SPLAT_RADIUS={0.35}
          SPLAT_FORCE={6000}
          DENSITY_DISSIPATION={2.5}
          CURL={30}
          TRANSPARENT={true}
          COLOR_UPDATE_SPEED={12}
        />
      </div>

      <div className="relative z-10">
        <Navbar />
        
        <div className="container max-w-3xl mx-auto py-12 px-4">
          {!isSubmitted ? (
            <>
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-white">{texts.title}</h1>
                <p className="text-white/70 mt-2">{texts.subtitle}</p>
              </div>

              <div className="bg-white/5 rounded-lg border border-white/10 p-6 md:p-8">
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div className="space-y-2">
                      <Label htmlFor="fullName" className="text-white">{texts.fullName}</Label>
                      <Input
                        id="fullName"
                        name="fullName"
                        value={formData.fullName}
                        onChange={handleInputChange}
                        required
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="companyName" className="text-white">{texts.companyName}</Label>
                      <Input
                        id="companyName"
                        name="companyName"
                        value={formData.companyName}
                        onChange={handleInputChange}
                        required
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-white">{texts.email}</Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        required
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="phoneNumber" className="text-white">{texts.phoneNumber}</Label>
                      <Input
                        id="phoneNumber"
                        name="phoneNumber"
                        type="tel"
                        value={formData.phoneNumber}
                        onChange={handleInputChange}
                        required
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="message" className="text-white">{texts.message}</Label>
                    <Textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleInputChange}
                      placeholder={texts.messagePlaceholder}
                      className="bg-white/5 border-white/10 text-white min-h-[120px]"
                    />
                  </div>
                  
                  <div className="pt-4">
                    <Button 
                      type="submit" 
                      className="w-full bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90 font-medium"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? texts.submitting : texts.submitButton}
                    </Button>
                  </div>
                </form>
              </div>
            </>
          ) : (
            <div className="bg-white/5 rounded-lg border border-white/10 p-8 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#6ACBDF]/20 mb-6">
                <svg className="w-8 h-8 text-[#6ACBDF]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white mb-4">{texts.successTitle}</h2>
              <p className="text-white/70 mb-8">{texts.successMessage}</p>
              <Button 
                onClick={() => router.push('/')}
                className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90 font-medium"
              >
                {texts.backToHome}
              </Button>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
