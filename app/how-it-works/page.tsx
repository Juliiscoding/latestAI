import Navbar from "@/components/navbar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { StarField } from "@/components/star-field"
import { SparklesCore } from "@/components/sparkles"
import { Upload, Database, Cpu, BarChart, Lightbulb, Rocket } from "lucide-react"
import Link from "next/link"

const steps = [
  {
    title: "Data Upload",
    description:
      "Securely upload your business data through our intuitive interface or connect directly to your existing data sources.",
    icon: Upload,
  },
  {
    title: "Data Processing",
    description:
      "Our advanced algorithms clean, structure, and prepare your data for analysis, ensuring accuracy and consistency.",
    icon: Database,
  },
  {
    title: "AI Analysis",
    description:
      "Powerful machine learning models analyze your data, uncovering patterns, trends, and insights that humans might miss.",
    icon: Cpu,
  },
  {
    title: "Visualization",
    description:
      "Complex data is transformed into clear, interactive visualizations that make it easy to understand and act upon.",
    icon: BarChart,
  },
  {
    title: "Insight Generation",
    description:
      "Receive actionable insights and recommendations tailored to your business goals and industry benchmarks.",
    icon: Lightbulb,
  },
  {
    title: "Implementation",
    description:
      "Put your insights into action with our guided implementation tools and track the results in real-time.",
    icon: Rocket,
  },
]

export default function HowItWorksPage() {
  return (
    <div className="min-h-screen bg-black antialiased relative overflow-hidden">
      {/* Background Effects */}
      <StarField />
      <div className="absolute inset-0 z-[1] opacity-50">
        <SparklesCore
          id="tsparticleshowitworks"
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
              How{" "}
              <span className="bg-gradient-to-r from-[#6ACBDF] to-[#AA0E33] bg-clip-text text-transparent">
                Mercurios.ai
              </span>{" "}
              Works
            </h1>
            <p className="text-xl text-white/60 max-w-3xl mx-auto">
              Discover the simple yet powerful process that turns your raw data into actionable business insights.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {steps.map((step, index) => (
              <Card key={index} className="bg-white/10 border-white/20 text-white relative overflow-hidden">
                <div className="absolute top-0 right-0 bg-[#6ACBDF] text-black font-bold px-3 py-1 rounded-bl-lg">
                  Step {index + 1}
                </div>
                <CardHeader>
                  <step.icon className="h-10 w-10 mb-3 text-[#6ACBDF]" />
                  <CardTitle>{step.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-white/60">{step.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="mt-20 text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">Ready to Transform Your Data?</h2>
            <Link href="/signup">
              <Button size="lg" className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">
                Start Your Journey
              </Button>
            </Link>
          </div>
        </main>
      </div>
    </div>
  )
}

