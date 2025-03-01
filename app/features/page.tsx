import Navbar from "@/components/navbar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { StarField } from "@/components/star-field"
import { SparklesCore } from "@/components/sparkles"
import { BarChart3, Brain, Zap, Users, TrendingUp, Lock } from "lucide-react"
import Link from "next/link"

const features = [
  {
    title: "AI-Powered Insights",
    description: "Leverage advanced machine learning algorithms to uncover hidden patterns and trends in your data.",
    icon: Brain,
  },
  {
    title: "Real-Time Analytics",
    description: "Get up-to-the-minute insights with our lightning-fast data processing engine.",
    icon: Zap,
  },
  {
    title: "Customizable Dashboards",
    description: "Create personalized dashboards tailored to your specific business needs and KPIs.",
    icon: BarChart3,
  },
  {
    title: "Collaborative Tools",
    description: "Share insights and work together with your team in real-time.",
    icon: Users,
  },
  {
    title: "Predictive Analytics",
    description: "Forecast future trends and make data-driven decisions with our predictive models.",
    icon: TrendingUp,
  },
  {
    title: "Enterprise-Grade Security",
    description: "Rest easy knowing your data is protected with state-of-the-art security measures.",
    icon: Lock,
  },
]

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-black antialiased relative overflow-hidden">
      {/* Background Effects */}
      <StarField />
      <div className="absolute inset-0 z-[1] opacity-50">
        <SparklesCore
          id="tsparticlesfeatures"
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
              Powerful Features for{" "}
              <span className="bg-gradient-to-r from-[#6ACBDF] to-[#AA0E33] bg-clip-text text-transparent">
                Data-Driven Decisions
              </span>
            </h1>
            <p className="text-xl text-white/60 max-w-3xl mx-auto">
              Discover how Mercurios.ai can transform your business with cutting-edge AI analytics tools.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
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

          <div className="mt-20 text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">Ready to Get Started?</h2>
            <Link href="/signup">
              <Button size="lg" className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">
                Start Your Free Trial
              </Button>
            </Link>
          </div>
        </main>
      </div>
    </div>
  )
}

