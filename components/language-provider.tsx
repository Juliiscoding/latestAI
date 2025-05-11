"use client"
import { ReactNode, useState, useEffect } from "react"
import { LanguageContext } from "./footer"

interface LanguageProviderProps {
  children: ReactNode
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [language, setLanguage] = useState('de')
  
  useEffect(() => {
    // Get stored language preference on client side
    const storedLanguage = localStorage.getItem('language') || 'de'
    setLanguage(storedLanguage)
  }, [])
  
  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  )
}
