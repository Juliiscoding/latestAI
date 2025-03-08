"use client"
import Link from "next/link"
import { Button as DefaultButton } from "@/components/ui/button"
import { useState } from "react"
import { Menu, X, Wrench, Lightbulb, BookOpen, DollarSign, LogIn } from "lucide-react"
import { usePathname } from "next/navigation"
import { HoverExpandableTabs } from "@/components/ui/hover-expandable-tabs"
import { Button as MovingBorderButton } from "@/components/ui/moving-border"

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const pathname = usePathname()

  const isActive = (path: string) => pathname === path
  
  const tabs = [
    { title: "FEATURES", icon: Wrench, href: "/features" },
    { title: "HOW IT WORKS", icon: Lightbulb, href: "/how-it-works" },
    { title: "EXAMPLES", icon: BookOpen, href: "/examples" },
    { title: "PRICING", icon: DollarSign, href: "/pricing" },
  ]

  return (
    <div className="w-full border-b border-white/10 relative">
      <nav className="container flex h-20 items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center space-x-2 z-10">
          <img
            src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/MercuriosAI_MainLogo_RGB_300dpi-ZRorxeuhkpRJKVtuxIiQl9y6tiqpLE.png"
            alt="Mercurios.ai Logo"
            className="h-8 sm:h-10 md:h-12"
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
        <div className="hidden md:flex items-center justify-center absolute left-1/2 transform -translate-x-1/2 space-x-2 lg:space-x-6">
          <HoverExpandableTabs 
            tabs={tabs} 
            className="bg-transparent shadow-none text-base lg:text-lg" 
            activeColor="text-[#6ACBDF]"
          />
        </div>

        {/* Login/Signup buttons */}
        <div className="hidden md:flex items-center space-x-3 lg:space-x-5 z-10">
          <Link href="/login">
            <MovingBorderButton 
              borderRadius="0.5rem" 
              className="bg-black/50 text-white text-sm md:text-base h-10 md:h-12 w-24 md:w-28 hover:text-[#6ACBDF]"
              containerClassName="h-10 md:h-12 w-24 md:w-28"
              borderClassName="bg-[radial-gradient(var(--cyan-500)_40%,transparent_60%)]"
            >
              Log In
            </MovingBorderButton>
          </Link>
          <Link href="/signup">
            <MovingBorderButton 
              borderRadius="0.5rem" 
              className="bg-[#6ACBDF]/80 text-black text-sm md:text-base font-medium h-10 md:h-12 w-32 md:w-36 hover:bg-[#6ACBDF]" 
              containerClassName="h-10 md:h-12 w-32 md:w-36"
              borderClassName="bg-[radial-gradient(var(--cyan-300)_40%,transparent_60%)]"
            >
              Get Started
            </MovingBorderButton>
          </Link>
        </div>
      </nav>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-black/95 fixed top-20 left-0 right-0 bottom-0 z-50 overflow-y-auto">
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

