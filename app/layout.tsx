import { Inter } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { TenantProvider } from "@/lib/mercurios/tenant-context"
import type React from "react"
import dynamic from "next/dynamic"

const Footer = dynamic(() => import("@/components/footer"), { ssr: true })
const SplashCursor = dynamic(() => import("@/components/ui/splash-cursor").then(mod => ({ default: mod.SplashCursor })), { ssr: false })
const LanguageProvider = dynamic(() => import("@/components/language-provider").then(mod => ({ default: mod.LanguageProvider })), { ssr: false })

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "Mercurios.ai",
  description: "AI-powered solutions for retail and e-commerce",
  generator: "Next.js",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head />
      <body className={`${inter.className} antialiased min-h-screen transition-colors duration-300 flex flex-col bg-black`}>
        <TenantProvider>
          <Providers>
            <LanguageProvider>
              {/* Cursor animation that appears on all pages */}
              <SplashCursor 
                TRANSPARENT={true} 
                BACK_COLOR={{ r: 0.1, g: 0.1, b: 0.1 }} 
                DENSITY_DISSIPATION={3.5}
                VELOCITY_DISSIPATION={2.2}
                SPLAT_RADIUS={0.2}
                CURL={3}
              />
              <div className="flex flex-col min-h-screen relative z-10">
                <main className="flex-grow">{children}</main>
                <Footer />
              </div>
            </LanguageProvider>
          </Providers>
        </TenantProvider>
      </body>
    </html>
  )
}