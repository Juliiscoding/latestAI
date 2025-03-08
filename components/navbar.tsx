"use client"
import Link from "next/link"
import { Button as DefaultButton } from "@/components/ui/button"
import { useState, useEffect } from "react"
import { Menu, X, Wrench, Lightbulb, BookOpen, DollarSign, LogIn } from "lucide-react"
import { usePathname } from "next/navigation"
import { HoverExpandableTabs } from "@/components/ui/hover-expandable-tabs"
import { Button as MovingBorderButton } from "@/components/ui/moving-border"

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1200,
    height: typeof window !== 'undefined' ? window.innerHeight : 800
  })
  const [isCompact, setIsCompact] = useState(false)
  const pathname = usePathname()
  
  // Update screen size when window resizes
  useEffect(() => {
    const handleResize = () => {
      setScreenSize({
        width: window.innerWidth,
        height: window.innerHeight
      })
      setIsCompact(window.innerWidth < 1024)
    }
    
    // Set initial value
    handleResize()
    
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const isActive = (path: string) => pathname === path
  
  const tabs = [
    { title: "FEATURES", icon: Wrench, href: "/features" },
    { title: "HOW IT WORKS", icon: Lightbulb, href: "/how-it-works" },
    { title: "EXAMPLES", icon: BookOpen, href: "/examples" },
    { title: "PRICING", icon: DollarSign, href: "/pricing" },
  ]

  return (
    <div className="w-full border-b border-white/10 relative">
      <nav className="container flex items-center px-2 sm:px-4 lg:px-6" 
        style={{
          height: screenSize.width < 640 ? '60px' : 
                 screenSize.width < 1024 ? '70px' : '80px',
          justifyContent: 'space-between',
          maxWidth: '100%',
          overflow: 'hidden'
        }}>
        <Link href="/" className="flex items-center z-10 flex-shrink-0">
          <img
            src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/MercuriosAI_MainLogo_RGB_300dpi-ZRorxeuhkpRJKVtuxIiQl9y6tiqpLE.png"
            alt="Mercurios.ai Logo"
            style={{
              height: screenSize.width < 640 ? '26px' : 
                     screenSize.width < 768 ? '30px' : 
                     screenSize.width < 1024 ? '34px' : '38px',
              marginRight: screenSize.width < 640 ? '4px' : '8px'
            }}
          />
        </Link>

        {/* Mobile menu toggle button */}
        <div className="md:hidden z-10">
          <button 
            className="text-white p-2" 
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle menu"
          >
            {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
          </button>
        </div>

        {/* Desktop menu with hover expandable tabs */}
        <div 
          className="hidden md:flex items-center justify-center flex-grow"
          style={{
            position: 'relative',
            marginLeft: screenSize.width < 768 ? '4px' : '8px',
            marginRight: screenSize.width < 768 ? '4px' : '8px',
          }}
        >
          <HoverExpandableTabs 
            tabs={tabs} 
            className="bg-transparent shadow-none text-base lg:text-lg w-full justify-center" 
            activeColor="text-[#6ACBDF]"
          />
        </div>

        {/* Login/Signup buttons */}
        <div className="hidden md:flex items-center z-10 flex-shrink-0"
          style={{
            gap: screenSize.width < 768 ? '4px' : screenSize.width < 1024 ? '8px' : '12px'
          }}
        >
          <Link href="/login">
            <MovingBorderButton 
              borderRadius="0.5rem" 
              className="bg-black/50 text-white hover:text-[#6ACBDF]"
              containerClassName={`${screenSize.width < 768 ? 'h-8 w-16 text-xs' : screenSize.width < 1024 ? 'h-9 w-20 text-xs' : screenSize.width < 1280 ? 'h-10 w-24 text-sm' : 'h-12 w-28 text-base'}`}
              borderClassName="bg-[radial-gradient(var(--cyan-500)_40%,transparent_60%)]"
            >
              Log In
            </MovingBorderButton>
          </Link>
          <Link href="/signup">
            <MovingBorderButton 
              borderRadius="0.5rem" 
              className="bg-[#6ACBDF]/80 text-black font-medium hover:bg-[#6ACBDF]" 
              containerClassName={`${screenSize.width < 768 ? 'h-8 w-24 text-xs' : screenSize.width < 1024 ? 'h-9 w-28 text-xs' : screenSize.width < 1280 ? 'h-10 w-32 text-sm' : 'h-12 w-36 text-base'}`}
              borderClassName="bg-[radial-gradient(var(--cyan-300)_40%,transparent_60%)]"
            >
              Get Started
            </MovingBorderButton>
          </Link>
        </div>
      </nav>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-black/95 fixed left-0 right-0 bottom-0 z-50 overflow-y-auto"
          style={{ top: screenSize.width < 640 ? '60px' : '70px' }}>
          <div className="flex flex-col items-center space-y-6 py-8 px-4">
            {tabs.map((tab, index) => {
              const Icon = tab.icon;
              return (
                <Link
                  key={tab.title}
                  href={tab.href}
                  className={`flex items-center space-x-3 text-lg text-white transition-all duration-300 hover:text-[#6ACBDF] ${isActive(tab.href) ? "text-[#6ACBDF] font-bold" : ""}`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  <Icon size={24} />
                  <span>{tab.title}</span>
                </Link>
              );
            })}
            
            <div className="w-full h-px bg-white/10 my-2"></div>
            
            <Link href="/login" className="w-full max-w-xs" onClick={() => setIsMenuOpen(false)}>
              <MovingBorderButton 
                borderRadius="0.5rem" 
                className="bg-black/50 text-white text-base h-12 w-full hover:text-[#6ACBDF]"
                containerClassName="h-12 w-full"
                borderClassName="bg-[radial-gradient(var(--cyan-500)_40%,transparent_60%)]"
              >
                Log In
              </MovingBorderButton>
            </Link>
            <Link href="/signup" className="w-full max-w-xs" onClick={() => setIsMenuOpen(false)}>
              <MovingBorderButton 
                borderRadius="0.5rem" 
                className="bg-[#6ACBDF]/80 text-black text-base font-medium h-12 w-full hover:bg-[#6ACBDF]" 
                containerClassName="h-12 w-full"
                borderClassName="bg-[radial-gradient(var(--cyan-300)_40%,transparent_60%)]"
              >
                Get Started
              </MovingBorderButton>
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

