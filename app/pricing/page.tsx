import Navbar from "@/components/navbar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { StarField } from "@/components/star-field"
import { SparklesCore } from "@/components/sparkles"
import { Check, X } from "lucide-react"
import Link from "next/link"

const pricingPlans = [
  {
    name: "Starter",
    price: "€49",
    description: "Perfect for small businesses and startups",
    features: [
      "Up to 5,000 data points per month",
      "Basic AI-powered insights",
      "5 custom dashboards",
      "Email support",
      "Data retention for 3 months",
    ],
    limitations: ["No API access", "No custom integrations", "No team collaboration tools"],
  },
  {
    name: "Pro",
    price: "€199",
    description: "Ideal for growing companies with advanced needs",
    features: [
      "Up to 50,000 data points per month",
      "Advanced AI-powered insights",
      "Unlimited custom dashboards",
      "Priority email and chat support",
      "Data retention for 12 months",
      "API access",
      "Custom integrations",
      "Team collaboration tools",
    ],
    limitations: ["No dedicated account manager", "No on-premise deployment"],
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "Tailored solutions for large organizations",
    features: [
      "Unlimited data points",
      "Enterprise-grade AI insights",
      "Unlimited custom dashboards",
      "24/7 phone, email, and chat support",
      "Unlimited data retention",
      "Full API access",
      "Custom integrations",
      "Advanced team collaboration tools",
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
      {/* Background Effects */}
      <StarField />
      <div className="absolute inset-0 z-[1] opacity-50">
        <SparklesCore
          id="tsparticlespricing"
          background="transparent"
          minSize={0.2}
          maxSize={0.6}
          particleDensity={100}
          className="w-full h-full"
          particleColor="#FFFFFF"
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
                    <Button size="lg" className="w-full bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">
                      {plan.name === "Enterprise" ? "Contact Sales" : "Get Started"}
                    </Button>
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
              <Button size="lg" variant="outline" className="text-white border-white/20 hover:bg-white/10">
                Schedule a Consultation
              </Button>
            </Link>
          </div>
        </main>
      </div>
    </div>
  )
}

