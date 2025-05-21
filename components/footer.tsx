"use client"
import Link from "next/link"
import { useState, useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useLanguage } from "./language-provider"

export default function Footer() {
  const router = useRouter();
  const pathname = usePathname();
  const { language, setLanguage } = useLanguage();
  
  // Handle language change
  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLanguage = e.target.value;
    setLanguage(newLanguage);
    
    // Redirect to the equivalent page in the new language
    // This is a simple implementation - for a real site you'd need proper i18n routing
    if (newLanguage === 'en') {
      // Map German paths to English paths
      const pathMap: {[key: string]: string} = {
        '/legal/impressum': '/legal/imprint',
        '/legal/datenschutz': '/legal/privacy-policy',
        '/legal/agb': '/legal/terms',
        '/legal/cookie-policy': '/legal/cookie-policy',
        '/legal/widerrufsrecht': '/legal/right-of-withdrawal'
      };
      
      // Check if current path has an English equivalent
      if (pathname) {
        const newPath = pathMap[pathname] || pathname;
        router.push(newPath);
      }
    }
  };
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1200,
    height: typeof window !== 'undefined' ? window.innerHeight : 800
  })
  
  // Update screen size when window resizes
  useEffect(() => {
    const handleResize = () => {
      setScreenSize({
        width: window.innerWidth,
        height: window.innerHeight
      })
    }
    
    // Set initial value
    handleResize()
    
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Footer links for legal compliance
  const legalLinks = [
    { title: "Impressum", href: "/legal/impressum" },
    { title: "Datenschutz", href: "/legal/datenschutz" },
    { title: "AGB", href: "/legal/agb" },
    { title: "Cookie-Richtlinie", href: "/legal/cookie-policy" },
    { title: "Widerrufsrecht", href: "/legal/widerrufsrecht" }
  ]

  // Company links
  const companyLinks = [
    { title: "Über uns", href: "/about" },
    { title: "Kontakt", href: "/contact" }
  ]

  return (
    <footer className="w-full border-t border-white/10 bg-transparent mt-auto relative overflow-hidden">
      {/* Gradient overlay for seamless transition */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/80 to-black backdrop-blur-md z-0"></div>
      
      <div className="container relative mx-auto px-4 py-8 z-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Company Info */}
          <div>
            <Link href="/" className="flex items-center mb-4">
              <img
                src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/MercuriosAI_MainLogo_RGB_300dpi-ZRorxeuhkpRJKVtuxIiQl9y6tiqpLE.png"
                alt="Mercurios.ai Logo"
                style={{
                  height: screenSize.width < 640 ? '24px' : '30px'
                }}
              />
            </Link>
            <p className="text-white/90 text-sm font-medium">
              Mercurios.ai transformiert Ihre Einzelhandelsdaten in umsetzbare Erkenntnisse. 
              Unsere KI-gestützte Plattform liefert leistungsstarke Analysen und KI-generierte 
              Inhalte, um Ihren Umsatz zu steigern und Abläufe zu optimieren.
            </p>
            <div className="mt-4 flex space-x-4">
              <a href="https://twitter.com/mercuriosai" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
                <svg className="h-5 w-5 text-white hover:text-[#6ACBDF]" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
              <a href="https://linkedin.com/company/mercuriosai" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                <svg className="h-5 w-5 text-white hover:text-[#6ACBDF]" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                </svg>
              </a>
            </div>
          </div>
          
          {/* Company Links */}
          <div>
            <h3 className="text-white text-lg font-semibold mb-4">{language === 'de' ? 'Unternehmen' : 'Company'}</h3>
            <ul className="space-y-2">
              {companyLinks.map((link) => (
                <li key={link.title}>
                  <Link 
                    href={link.href} 
                    className="text-white hover:text-[#6ACBDF] transition-colors text-sm font-medium"
                  >
                    {link.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Legal Links */}
          <div>
            <h3 className="text-white text-lg font-semibold mb-4">{language === 'de' ? 'Rechtliches' : 'Legal'}</h3>
            <ul className="space-y-2">
              {legalLinks.map((link) => (
                <li key={link.title}>
                  <Link 
                    href={link.href} 
                    className="text-white hover:text-[#6ACBDF] transition-colors text-sm font-medium"
                  >
                    {link.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
        
        <div className="border-t border-white/10 mt-8 pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-white/80 text-xs">
              © {new Date().getFullYear()} Mercurios.ai. {language === 'de' ? 'Alle Rechte vorbehalten.' : 'All rights reserved.'}
            </p>
            <div className="mt-4 md:mt-0">
              <select 
                className="bg-black/80 text-white/90 text-xs border border-white/30 rounded-md px-2 py-1 font-medium"
                value={language}
                onChange={handleLanguageChange}
              >
                <option value="de">Deutsch</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
