import Navbar from "@/components/navbar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SplashCursor } from "@/components/ui/splash-cursor"
import { 
  BarChart3, 
  Brain, 
  Zap, 
  ShoppingBag, 
  Database, 
  ShoppingCart, 
  Image, 
  FileText, 
  CreditCard, 
  Layers,
  Lock,
  Sparkles
} from "lucide-react"
import Link from "next/link"

const retailAnalyticsFeatures = [
  {
    title: "ProHandel Integration",
    description: "Connect directly to your ProHandel POS system with our secure AWS Lambda connector.",
    icon: ShoppingBag,
  },
  {
    title: "Multi-Tenant Data Warehouse",
    description: "Enterprise-grade Snowflake data warehouse with role-based access control and tenant isolation.",
    icon: Database,
  },
  {
    title: "Comprehensive Data Sync",
    description: "Automatically sync articles, customers, orders, sales, and inventory data from ProHandel.",
    icon: Layers,
  },
  {
    title: "Real-Time Analytics",
    description: "Get up-to-the-minute insights with our lightning-fast data processing engine.",
    icon: Zap,
  },
  {
    title: "Customizable Dashboards",
    description: "Create personalized dashboards tailored to your specific retail business needs and KPIs.",
    icon: BarChart3,
  },
  {
    title: "Enterprise-Grade Security",
    description: "Rest easy knowing your data is protected with state-of-the-art security measures and AWS Secrets Manager.",
    icon: Lock,
  },
]

const shopifyAppFeatures = [
  {
    title: "AI Product Descriptions",
    description: "Generate SEO-optimized product descriptions in multiple languages with our Mistral-powered AI.",
    icon: FileText,
  },
  {
    title: "AI Alt Text Generation",
    description: "Create accessible and SEO-friendly alt text for product images automatically.",
    icon: Image,
  },
  {
    title: "Bulk Generation",
    description: "Process multiple products at once based on categories or product types (Enterprise plan).",
    icon: Sparkles,
  },
  {
    title: "Shopify Integration",
    description: "Seamlessly integrates with your Shopify Admin API for product and image management.",
    icon: ShoppingCart,
  },
  {
    title: "Flexible Subscription Plans",
    description: "Choose from Basic, Pro, or Enterprise plans to match your business needs and budget.",
    icon: CreditCard,
  },
  {
    title: "AI-Powered Insights",
    description: "Leverage advanced machine learning algorithms to enhance your product content.",
    icon: Brain,
  },
]

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-black antialiased relative overflow-hidden">
      {/* Splash cursor background effect */}
      <div className="absolute inset-0 z-0">
        <SplashCursor 
          BACK_COLOR={{ r: 0, g: 0, b: 0 }}
          SPLAT_RADIUS={0.3}
          SPLAT_FORCE={8000}
          DENSITY_DISSIPATION={3}
          CURL={20}
          TRANSPARENT={true}
        />
      </div>

      <div className="relative z-10">
        <Navbar />

        <main className="container mx-auto px-4 py-16 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-4">
              Powerful Features for{" "}
              <span className="bg-gradient-to-r from-[#6ACBDF] to-[#AA0E33] bg-clip-text text-transparent">
                Data-Driven Decisions
              </span>
            </h1>
            <p className="text-xl text-white/60 max-w-3xl mx-auto">
              Discover how Mercurios.ai can transform your business with cutting-edge AI analytics tools.
            </p>
          </div>

          {/* Retail Analytics Platform Section */}
          <div className="mb-20">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">
              <span className="bg-gradient-to-r from-[#6ACBDF] to-[#AA0E33] bg-clip-text text-transparent">
                Retail Analytics Platform
              </span>
            </h2>
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {retailAnalyticsFeatures.map((feature, index) => (
                <Card key={index} className="bg-white/10 border-white/20 text-white">
                  <CardHeader>
                    <feature.icon className="h-10 w-10 mb-3 text-[#6ACBDF]" />
                    <CardTitle>{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-white/60">{feature.description}</CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Shopify App Section */}
          <div className="mb-20">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">
              <span className="bg-gradient-to-r from-[#6ACBDF] to-[#AA0E33] bg-clip-text text-transparent">
                Shopify AI Content Generator
              </span>
            </h2>
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {shopifyAppFeatures.map((feature, index) => (
                <Card key={index} className="bg-white/10 border-white/20 text-white">
                  <CardHeader>
                    <feature.icon className="h-10 w-10 mb-3 text-[#6ACBDF]" />
                    <CardTitle>{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-white/60">{feature.description}</CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          <div className="mt-20 text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">Ready to Get Started?</h2>
            <Link href="/pricing">
              <Button size="lg" className="bg-gradient-to-r from-[#6ACBDF] to-[#AA0E33] text-white transition-all duration-300 hover:shadow-[0_0_20px_rgba(170,14,51,0.7)] hover:scale-105">
                View Pricing Plans
              </Button>
            </Link>
          </div>
        </main>
      </div>
    </div>
  )
}

