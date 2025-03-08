import Navbar from "@/components/navbar"
import { Button } from "@/components/ui/button"
import { Button as MovingBorderButton } from "@/components/ui/moving-border"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { SplashCursor } from "@/components/ui/splash-cursor"
import { Check, X } from "lucide-react"
import Link from "next/link"

const pricingPlans = [
  {
    name: "Shopify Basic",
    price: "$9.99",
    period: "per month",
    description: "Essential AI tools for Shopify store owners",
    features: [
      "AI Product Descriptions",
      "5 languages supported",
      "100 descriptions per month",
      "Email support",
      "Basic SEO optimization",
    ],
    limitations: ["No alt text generation", "Limited language options", "No bulk generation"],
    popular: false,
    color: "from-blue-400 to-blue-600",
  },
  {
    name: "Shopify Pro",
    price: "$19.99",
    period: "per month",
    description: "Advanced AI tools for growing Shopify stores",
    features: [
      "AI Product Descriptions",
      "AI Alt Text Generation",
      "All languages supported",
      "500 generations per month",
      "Priority email and chat support",
      "Advanced SEO optimization",
    ],
    limitations: ["No bulk generation", "No custom AI training"],
    popular: true,
    color: "from-[#6ACBDF] to-[#AA0E33]",
  },
  {
    name: "Shopify Enterprise",
    price: "$49.99",
    period: "per month",
    description: "Complete AI solution for high-volume Shopify stores",
    features: [
      "All Pro features",
      "Bulk generation capabilities",
      "Custom AI training",
      "Unlimited generations",
      "Dedicated account manager",
      "Custom integrations",
      "Advanced analytics dashboard",
    ],
    limitations: [],
    popular: false,
    color: "from-purple-500 to-purple-700",
  },
  {
    name: "Retail Analytics",
    price: "Custom",
    period: "",
    description: "Enterprise retail analytics platform for ProHandel & Shopify",
    features: [
      "Multi-tenant data warehouse (Snowflake)",
      "ProHandel API integration",
      "Shopify integration",
      "Custom dashboards and reports",
      "Real-time analytics",
      "Data retention for 24 months",
      "Dedicated implementation team",
      "24/7 premium support",
      "Dedicated account manager",
      "On-premise deployment option",
      "Custom AI model training",
    ],
    limitations: [],
  },
]

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-black antialiased relative overflow-hidden">
      {/* Splash cursor background effect */}
      <div className="absolute inset-0 z-0">
        <SplashCursor 
          BACK_COLOR={{ r: 0, g: 0, b: 0 }}
          SPLAT_RADIUS={0.35}
          SPLAT_FORCE={6000}
          DENSITY_DISSIPATION={2.5}
          CURL={30}
          TRANSPARENT={true}
          COLOR_UPDATE_SPEED={12}
        />
      </div>

      <div className="relative z-10">
        <Navbar />

        <main className="container mx-auto px-4 py-16 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-4">
              Choose the Right Plan for Your{" "}
              <span className="bg-gradient-to-r from-[#6ACBDF] to-[#AA0E33] bg-clip-text text-transparent">
                Business
              </span>
            </h1>
            <p className="text-xl text-white/60 max-w-3xl mx-auto">
              Flexible pricing options to suit businesses of all sizes. Unlock the power of AI-driven analytics today.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {pricingPlans.map((plan, index) => (
              <Card key={index} className="bg-white/10 border-white/20 text-white flex flex-col">
                <CardHeader>
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <CardDescription className="text-white/60">{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex-grow">
                  <p className="text-4xl font-bold mb-6">
                    {plan.price}
                    <span className="text-lg font-normal">{plan.price !== "Custom" && "/month"}</span>
                  </p>
                  <ul className="space-y-2">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center">
                        <Check className="h-5 w-5 text-[#6ACBDF] mr-2" />
                        <span>{feature}</span>
                      </li>
                    ))}
                    {plan.limitations.map((limitation, limitationIndex) => (
                      <li key={limitationIndex} className="flex items-center text-white/40">
                        <X className="h-5 w-5 text-red-500 mr-2" />
                        <span>{limitation}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter>
                  <Link href="/signup" className="w-full">
                    <MovingBorderButton 
                      borderRadius="0.5rem" 
                      className="bg-[#6ACBDF]/80 text-black font-medium hover:bg-[#6ACBDF] w-full" 
                      containerClassName="w-full h-12"
                      borderClassName="bg-[radial-gradient(var(--cyan-300)_40%,transparent_60%)]"
                    >
                      {plan.name === "Enterprise" ? "Contact Sales" : "Start Free Trial"}
                    </MovingBorderButton>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>

          <div className="mt-20 text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">Not Sure Which Plan to Choose?</h2>
            <p className="text-xl text-white/60 max-w-3xl mx-auto mb-8">
              Our team of experts is here to help you find the perfect solution for your business needs.
            </p>
            <Link href="/contact">
              <MovingBorderButton 
                borderRadius="0.5rem" 
                className="bg-black/50 text-white hover:text-[#6ACBDF]" 
                containerClassName="h-12 w-64"
                borderClassName="bg-[radial-gradient(var(--cyan-500)_40%,transparent_60%)]"
              >
                Book a Demo
              </MovingBorderButton>
            </Link>
          </div>
        </main>
      </div>
    </div>
  )
}

