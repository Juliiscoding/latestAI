import { Button } from "@/components/ui/button"
import Link from "next/link"
import { ArrowRight, ShoppingBag, BarChart, Zap } from "lucide-react"

export default function Hero() {
  return (
    <div className="container flex min-h-[calc(100vh-3.5rem)] items-center">
      <div className="relative z-10 mx-auto w-full max-w-4xl text-center">
        <div className="inline-block px-3 py-1 mb-6 rounded-full bg-white/10 backdrop-blur-sm border border-white/20">
          <p className="text-xs font-medium text-white/80 flex items-center">
            <span className="bg-gradient-to-r from-[#6ACBDF] to-[#AA0E33] bg-clip-text text-transparent font-bold">NEW</span>
            <span className="mx-2">|</span>
            <span>Retail Analytics Platform for ProHandel & Shopify</span>
          </p>
        </div>
        
        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-mono font-bold text-white">
          Unlock Retail Success with{" "}
          <span className="bg-gradient-to-r from-[#6ACBDF] to-[#AA0E33] bg-clip-text text-transparent">
            AI-Powered Insights
          </span>
        </h1>
        
        <p className="mx-auto mt-4 sm:mt-6 max-w-2xl text-sm sm:text-base md:text-lg text-white/70">
          Mercurios.ai transforms your retail data into actionable intelligence. Whether you use ProHandel or Shopify, 
          our platform delivers powerful analytics and AI-generated content to boost your sales and streamline operations.
        </p>
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto text-left">
          <div className="flex items-start space-x-3 bg-white/5 p-4 rounded-lg border border-white/10">
            <ShoppingBag className="h-6 w-6 text-[#6ACBDF]" />
            <div>
              <h3 className="font-medium text-white">Retail Analytics</h3>
              <p className="text-sm text-white/60">Comprehensive insights for ProHandel & Shopify stores</p>
            </div>
          </div>
          <div className="flex items-start space-x-3 bg-white/5 p-4 rounded-lg border border-white/10">
            <BarChart className="h-6 w-6 text-[#6ACBDF]" />
            <div>
              <h3 className="font-medium text-white">Data Warehouse</h3>
              <p className="text-sm text-white/60">Multi-tenant Snowflake integration</p>
            </div>
          </div>
          <div className="flex items-start space-x-3 bg-white/5 p-4 rounded-lg border border-white/10">
            <Zap className="h-6 w-6 text-[#6ACBDF]" />
            <div>
              <h3 className="font-medium text-white">AI Content</h3>
              <p className="text-sm text-white/60">Generate product descriptions & alt text</p>
            </div>
          </div>
        </div>
        
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Link href="/signup">
            <Button size="lg" className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90 font-medium">
              Start Free Trial <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link href="/demo">
            <Button size="lg" variant="outline" className="text-white border-white/20 bg-white/5 hover:bg-white/10">
              Book a Demo
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}

