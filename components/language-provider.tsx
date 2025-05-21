"use client"
import { ReactNode, useState, useEffect, useContext, createContext } from "react"

interface LanguageContextType {
  language: string;
  setLanguage: (lang: string) => void;
}

export const LanguageContext = createContext<LanguageContextType>({
  language: 'de',
  setLanguage: () => {}
});

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

export const useLanguage = () => useContext(LanguageContext);
