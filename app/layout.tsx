import { Inter } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { TenantProvider } from "@/lib/mercurios/tenant-context"
import type React from "react"

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
      <body className={`${inter.className} antialiased min-h-screen transition-colors duration-300`}>
        <TenantProvider>
          <Providers>{children}</Providers>
        </TenantProvider>
      </body>
    </html>
  )
}