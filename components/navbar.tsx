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

        {/* Mobile menu button */}
        <button className="md:hidden text-white" onClick={() => setIsMenuOpen(!isMenuOpen)}>
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Desktop menu */}
        <div className="hidden md:flex items-center space-x-8">
          <Link
            href="/features"
            className={`text-sm text-white hover:text-white/80 ${isActive("/features") ? "font-bold" : ""}`}
          >
            FEATURES
          </Link>
          <Link
            href="/how-it-works"
            className={`text-sm text-white hover:text-white/80 ${isActive("/how-it-works") ? "font-bold" : ""}`}
          >
            HOW IT WORKS
          </Link>
          <Link
            href="/examples"
            className={`text-sm text-white hover:text-white/80 ${isActive("/examples") ? "font-bold" : ""}`}
          >
            EXAMPLES
          </Link>
          <Link
            href="/pricing"
            className={`text-sm text-white hover:text-white/80 ${isActive("/pricing") ? "font-bold" : ""}`}
          >
            PRICING
          </Link>
        </div>
        <div className="hidden md:flex items-center space-x-4">
          <Link href="/login">
            <Button variant="ghost" className="text-white hover:text-black hover:bg-[#6ACBDF]">
              Log In
            </Button>
          </Link>
          <Link href="/signup">
            <Button className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">Get Started</Button>
          </Link>
        </div>
      </nav>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-black/95 absolute top-14 left-0 right-0 z-50">
          <div className="flex flex-col items-center space-y-4 py-4">
            <Link
              href="/features"
              className={`text-sm text-white hover:text-white/80 ${isActive("/features") ? "font-bold" : ""}`}
            >
              FEATURES
            </Link>
            <Link
              href="/how-it-works"
              className={`text-sm text-white hover:text-white/80 ${isActive("/how-it-works") ? "font-bold" : ""}`}
            >
              HOW IT WORKS
            </Link>
            <Link
              href="/examples"
              className={`text-sm text-white hover:text-white/80 ${isActive("/examples") ? "font-bold" : ""}`}
            >
              EXAMPLES
            </Link>
            <Link
              href="/pricing"
              className={`text-sm text-white hover:text-white/80 ${isActive("/pricing") ? "font-bold" : ""}`}
            >
              PRICING
            </Link>
            <Link href="/login">
              <Button variant="ghost" className="text-white hover:text-black hover:bg-[#6ACBDF]">
                Log In
              </Button>
            </Link>
            <Link href="/signup">
              <Button className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">Get Started</Button>
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

