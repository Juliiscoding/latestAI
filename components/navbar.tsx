"use client"
import Link from "next/link"
import { Button as DefaultButton } from "@/components/ui/button"
import { useState } from "react"
import { Menu, X, Wrench, Lightbulb, BookOpen, DollarSign, LogIn } from "lucide-react"
import { usePathname } from "next/navigation"
import { ExpandableTabs } from "@/components/ui/expandable-tabs"
import { Button as MovingBorderButton } from "@/components/ui/moving-border"

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const pathname = usePathname()
  const [activeTab, setActiveTab] = useState<number | null>(null)

  const isActive = (path: string) => pathname === path
  
  const tabs = [
    { title: "FEATURES", icon: Wrench },
    { title: "HOW IT WORKS", icon: Lightbulb },
    { title: "EXAMPLES", icon: BookOpen },
    { title: "PRICING", icon: DollarSign },
  ]
  
  const handleTabChange = (index: number | null) => {
    setActiveTab(index)
  }

  return (
    <div className="w-full border-b border-white/10">
      <nav className="container flex h-14 items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <img
            src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/MercuriosAI_MainLogo_RGB_300dpi-ZRorxeuhkpRJKVtuxIiQl9y6tiqpLE.png"
            alt="Mercurios.ai Logo"
            className="h-8"
          />
        </Link>

        {/* Mobile menu button - moved to right side with theme toggle */}

        {/* Desktop menu with expandable tabs */}
        <div className="hidden md:flex items-center">
          <ExpandableTabs 
            tabs={tabs} 
            className="bg-transparent border-none shadow-none" 
            activeColor="text-[#6ACBDF]"
            onChange={handleTabChange}
          />
          <div className="ml-2 flex space-x-2">
            {activeTab === 0 && (
              <Link href="/features">
                <DefaultButton variant="link" className="text-white hover:text-[#6ACBDF]">
                  View Features
                </DefaultButton>
              </Link>
            )}
            {activeTab === 1 && (
              <Link href="/how-it-works">
                <DefaultButton variant="link" className="text-white hover:text-[#6ACBDF]">
                  Learn More
                </DefaultButton>
              </Link>
            )}
            {activeTab === 2 && (
              <Link href="/examples">
                <DefaultButton variant="link" className="text-white hover:text-[#6ACBDF]">
                  See Examples
                </DefaultButton>
              </Link>
            )}
            {activeTab === 3 && (
              <Link href="/pricing">
                <DefaultButton variant="link" className="text-white hover:text-[#6ACBDF]">
                  View Plans
                </DefaultButton>
              </Link>
            )}
          </div>
        </div>
        <div className="hidden md:flex items-center space-x-4">
          <Link href="/login">
            <MovingBorderButton 
              borderRadius="0.5rem" 
              className="bg-black/50 text-white text-sm h-10 w-24 hover:text-[#6ACBDF]"
              containerClassName="h-10 w-24"
              borderClassName="bg-[radial-gradient(var(--cyan-500)_40%,transparent_60%)]"
            >
              Log In
            </MovingBorderButton>
          </Link>
          <Link href="/signup">
            <MovingBorderButton 
              borderRadius="0.5rem" 
              className="bg-[#6ACBDF]/80 text-black text-sm font-medium h-10 w-32 hover:bg-[#6ACBDF]" 
              containerClassName="h-10 w-32"
              borderClassName="bg-[radial-gradient(var(--cyan-300)_40%,transparent_60%)]"
            >
              Get Started
            </MovingBorderButton>
          </Link>
        </div>
      </nav>

      {/* Mobile menu toggle button */}
      <div className="md:hidden flex items-center space-x-2">
        <button className="text-white" onClick={() => setIsMenuOpen(!isMenuOpen)}>
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-black/95 absolute top-14 left-0 right-0 z-50">
          <div className="flex flex-col items-center space-y-4 py-4">
            <Link
              href="/features"
              className={`text-sm text-white transition-all duration-300 hover:text-[#6ACBDF] hover:scale-110 ${isActive("/features") ? "font-bold" : ""}`}
            >
              FEATURES
            </Link>
            <Link
              href="/how-it-works"
              className={`text-sm text-white transition-all duration-300 hover:text-[#6ACBDF] hover:scale-110 ${isActive("/how-it-works") ? "font-bold" : ""}`}
            >
              HOW IT WORKS
            </Link>
            <Link
              href="/examples"
              className={`text-sm text-white transition-all duration-300 hover:text-[#6ACBDF] hover:scale-110 ${isActive("/examples") ? "font-bold" : ""}`}
            >
              EXAMPLES
            </Link>
            <Link
              href="/pricing"
              className={`text-sm text-white transition-all duration-300 hover:text-[#6ACBDF] hover:scale-110 ${isActive("/pricing") ? "font-bold" : ""}`}
            >
              PRICING
            </Link>
            <Link href="/login">
              <MovingBorderButton 
                borderRadius="0.5rem" 
                className="bg-black/50 text-white text-sm h-10 w-24 hover:text-[#6ACBDF]"
                containerClassName="h-10 w-24"
                borderClassName="bg-[radial-gradient(var(--cyan-500)_40%,transparent_60%)]"
              >
                Log In
              </MovingBorderButton>
            </Link>
            <Link href="/signup">
              <MovingBorderButton 
                borderRadius="0.5rem" 
                className="bg-[#6ACBDF]/80 text-black text-sm font-medium h-10 w-32 hover:bg-[#6ACBDF]" 
                containerClassName="h-10 w-32"
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

