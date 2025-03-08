"use client"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useState } from "react"
import { Menu, X } from "lucide-react"
import { usePathname } from "next/navigation"

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const pathname = usePathname()

  const isActive = (path: string) => pathname === path

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

        {/* Desktop menu */}
        <div className="hidden md:flex items-center space-x-8">
          <Link
            href="/features"
            className={`text-sm text-white relative px-2 py-1 transition-all duration-300 ${isActive("/features") ? "font-bold" : ""}`}
          >
            <span className="relative z-10 group-hover:text-black">FEATURES</span>
            <span className="absolute inset-0 bg-[#6ACBDF] transform scale-x-0 origin-left transition-transform duration-300 ease-out group-hover:scale-x-100 hover:scale-x-100 opacity-0 hover:opacity-100 rounded-md"></span>
          </Link>
          <Link
            href="/how-it-works"
            className={`text-sm text-white relative px-2 py-1 transition-all duration-300 ${isActive("/how-it-works") ? "font-bold" : ""}`}
          >
            <span className="relative z-10 group-hover:text-black">HOW IT WORKS</span>
            <span className="absolute inset-0 bg-[#6ACBDF] transform scale-x-0 origin-left transition-transform duration-300 ease-out group-hover:scale-x-100 hover:scale-x-100 opacity-0 hover:opacity-100 rounded-md"></span>
          </Link>
          <Link
            href="/examples"
            className={`text-sm text-white relative px-2 py-1 transition-all duration-300 ${isActive("/examples") ? "font-bold" : ""}`}
          >
            <span className="relative z-10 group-hover:text-black">EXAMPLES</span>
            <span className="absolute inset-0 bg-[#6ACBDF] transform scale-x-0 origin-left transition-transform duration-300 ease-out group-hover:scale-x-100 hover:scale-x-100 opacity-0 hover:opacity-100 rounded-md"></span>
          </Link>
          <Link
            href="/pricing"
            className={`text-sm text-white relative px-2 py-1 transition-all duration-300 ${isActive("/pricing") ? "font-bold" : ""}`}
          >
            <span className="relative z-10 group-hover:text-black">PRICING</span>
            <span className="absolute inset-0 bg-[#6ACBDF] transform scale-x-0 origin-left transition-transform duration-300 ease-out group-hover:scale-x-100 hover:scale-x-100 opacity-0 hover:opacity-100 rounded-md"></span>
          </Link>
        </div>
        <div className="hidden md:flex items-center space-x-4">
          <Link href="/login">
            <Button variant="ghost" className="text-white hover:text-black hover:bg-[#6ACBDF] transition-all duration-300 hover:shadow-[0_0_15px_rgba(106,203,223,0.7)] hover:scale-105">
              Log In
            </Button>
          </Link>
          <Link href="/signup">
            <Button className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90 transition-all duration-300 hover:shadow-[0_0_15px_rgba(106,203,223,0.7)] hover:scale-105">Get Started</Button>
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
              <Button variant="ghost" className="text-white hover:text-black hover:bg-[#6ACBDF] transition-all duration-300 hover:shadow-[0_0_15px_rgba(106,203,223,0.7)] hover:scale-105">
                Log In
              </Button>
            </Link>
            <Link href="/signup">
              <Button className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90 transition-all duration-300 hover:shadow-[0_0_15px_rgba(106,203,223,0.7)] hover:scale-105">Get Started</Button>
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

