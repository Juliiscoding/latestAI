"use client"

import React from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import Link from "next/link"
import Image from "next/image"

export default function HyperionPage() {
  return (
    <div className="flex h-screen w-full overflow-hidden">
      <SidebarInset className="flex-1 overflow-auto w-full">
        <div className="w-full h-full p-4 sm:p-6 overflow-x-hidden">
          <header className="mb-6 flex items-center">
            <SidebarTrigger className="mr-4" />
            <h1 className="text-3xl font-bold">Hyperion Fashion AI</h1>
          </header>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="col-span-1 md:col-span-2">
              <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-semibold mb-2">Welcome to Hyperion Fashion AI</h2>
                    <p className="text-muted-foreground">
                      The centralized B2B platform for fashion brands and retailers
                    </p>
                  </div>
                  <Image
                    src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Screenshot%202025-02-25%20at%2019.31.53-mtfy43MfBuzK4cGsGUzDJo9O3cFY5s.png"
                    alt="Hyperion Fashion AI Logo"
                    width={200}
                    height={80}
                    className="object-contain"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-3">Product Data</h3>
              <p className="text-muted-foreground mb-4">
                Access up-to-date product information from multiple brands in one place.
              </p>
              <Link 
                href="/hyperion/product-data" 
                className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
              >
                Browse Products
              </Link>
            </div>
            
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-3">Marketing Media</h3>
              <p className="text-muted-foreground mb-4">
                Access high-quality marketing assets and media from your brand partners.
              </p>
              <Link 
                href="/hyperion/marketing-media" 
                className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
              >
                Browse Media
              </Link>
            </div>
            
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-3">Brands</h3>
              <p className="text-muted-foreground mb-4">
                Explore and connect with fashion brands on the Hyperion platform.
              </p>
              <Link 
                href="/hyperion/brands" 
                className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
              >
                View Brands
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-3">Latest Updates</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-2">
                  <span className="bg-primary/10 text-primary rounded-full p-1 mt-0.5">•</span>
                  <div>
                    <p className="font-medium">New Brands for Summer 2025</p>
                    <p className="text-sm text-muted-foreground">Discover the latest additions to our platform, including exciting new summer collections.</p>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <span className="bg-primary/10 text-primary rounded-full p-1 mt-0.5">•</span>
                  <div>
                    <p className="font-medium">Sustainability in Fashion</p>
                    <p className="text-sm text-muted-foreground">Learn about our initiatives to promote sustainable practices in the fashion industry.</p>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <span className="bg-primary/10 text-primary rounded-full p-1 mt-0.5">•</span>
                  <div>
                    <p className="font-medium">Upcoming Hyperion Fashion AI Connect Event</p>
                    <p className="text-sm text-muted-foreground">Join us for our next networking event and connect with industry leaders.</p>
                  </div>
                </li>
              </ul>
            </div>
            
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-3">Why Choose Hyperion Fashion AI?</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-2">
                  <span className="bg-primary/10 text-primary rounded-full p-1 mt-0.5">•</span>
                  <div>
                    <p className="font-medium">Centralized Product Data</p>
                    <p className="text-sm text-muted-foreground">Access up-to-date product information from multiple brands in one place.</p>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <span className="bg-primary/10 text-primary rounded-full p-1 mt-0.5">•</span>
                  <div>
                    <p className="font-medium">Efficient Ordering</p>
                    <p className="text-sm text-muted-foreground">Streamline your ordering process with our digital B2B platform.</p>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <span className="bg-primary/10 text-primary rounded-full p-1 mt-0.5">•</span>
                  <div>
                    <p className="font-medium">Industry Insights</p>
                    <p className="text-sm text-muted-foreground">Stay informed with the latest trends and analytics in the fashion industry.</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </SidebarInset>
    </div>
  )
}
