import { Inter } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import type React from "react"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "Mercurios.ai Dashboard",
  description: "Analytics dashboard for Mercurios.ai",
  generator: "v0.dev",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

import "./globals.css"

import "./globals.css"



import './globals.css'