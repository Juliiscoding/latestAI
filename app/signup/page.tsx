"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CheckCircle2, ArrowRight, ShoppingBag, BarChart, Zap } from "lucide-react"
import Navbar from "@/components/navbar"
import { SplashCursor } from "@/components/ui/splash-cursor"

export default function SignupPage() {
  const router = useRouter()
  const [selectedPlan, setSelectedPlan] = useState("basic")
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    companyName: "",
    fullName: "",
  })
  const [step, setStep] = useState(1)
  const [isLoading, setIsLoading] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handlePlanSelect = (plan: string) => {
    setSelectedPlan(plan)
  }

  const handleNextStep = () => {
    setStep(2)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false)
      router.push("/dashboard")
    }, 1500)
  }

  return (
    <main className="min-h-screen bg-black antialiased relative overflow-hidden">
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
        
        <div className="container max-w-6xl mx-auto py-12">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white">Get Started with Mercurios.ai</h1>
            <p className="text-white/70 mt-2">Create your account and start transforming your retail business</p>
          </div>

          <div className="flex justify-center">
            <div className="w-full max-w-3xl">
              <div className="flex items-center justify-center mb-8">
                <div className={`h-10 w-10 rounded-full flex items-center justify-center ${step >= 1 ? "bg-[#6ACBDF] text-black" : "bg-white/10 text-white"} font-bold`}>1</div>
                <div className={`h-1 w-16 ${step >= 2 ? "bg-[#6ACBDF]" : "bg-white/10"}`}></div>
                <div className={`h-10 w-10 rounded-full flex items-center justify-center ${step >= 2 ? "bg-[#6ACBDF] text-black" : "bg-white/10 text-white"} font-bold`}>2</div>
              </div>

              {step === 1 ? (
                <div className="bg-white/5 rounded-lg border border-white/10 p-6">
                  <h2 className="text-xl font-semibold text-white mb-6">Choose Your Plan</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <Card className={`bg-white/5 border ${selectedPlan === "basic" ? "border-[#6ACBDF]" : "border-white/10"} cursor-pointer transition-all hover:border-[#6ACBDF]/70`} onClick={() => handlePlanSelect("basic")}>
                      <CardHeader>
                        <CardTitle className="text-white">Basic</CardTitle>
                        <CardDescription className="text-white/70">For small businesses</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold text-white mb-4">$9.99<span className="text-sm font-normal text-white/70">/month</span></div>
                        <ul className="space-y-2">
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>AI Product Descriptions</span>
                          </li>
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>5 languages</span>
                          </li>
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>100 descriptions/month</span>
                          </li>
                        </ul>
                      </CardContent>
                    </Card>

                    <Card className={`bg-white/5 border ${selectedPlan === "pro" ? "border-[#6ACBDF]" : "border-white/10"} cursor-pointer transition-all hover:border-[#6ACBDF]/70`} onClick={() => handlePlanSelect("pro")}>
                      <CardHeader>
                        <CardTitle className="text-white">Pro</CardTitle>
                        <CardDescription className="text-white/70">For growing businesses</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold text-white mb-4">$19.99<span className="text-sm font-normal text-white/70">/month</span></div>
                        <ul className="space-y-2">
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>AI Product Descriptions</span>
                          </li>
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>AI Alt Text Generation</span>
                          </li>
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>All languages</span>
                          </li>
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>500 generations/month</span>
                          </li>
                        </ul>
                      </CardContent>
                    </Card>

                    <Card className={`bg-white/5 border ${selectedPlan === "enterprise" ? "border-[#6ACBDF]" : "border-white/10"} cursor-pointer transition-all hover:border-[#6ACBDF]/70`} onClick={() => handlePlanSelect("enterprise")}>
                      <CardHeader>
                        <CardTitle className="text-white">Enterprise</CardTitle>
                        <CardDescription className="text-white/70">For large businesses</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold text-white mb-4">$49.99<span className="text-sm font-normal text-white/70">/month</span></div>
                        <ul className="space-y-2">
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>All Pro features</span>
                          </li>
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>Bulk generation</span>
                          </li>
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>Custom AI training</span>
                          </li>
                          <li className="flex items-start gap-2 text-sm text-white/70">
                            <CheckCircle2 className="h-5 w-5 text-[#6ACBDF] flex-shrink-0" />
                            <span>Unlimited generations</span>
                          </li>
                        </ul>
                      </CardContent>
                    </Card>
                  </div>

                  <div className="flex justify-end">
                    <Button 
                      onClick={handleNextStep}
                      className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90"
                    >
                      Continue <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="bg-white/5 rounded-lg border border-white/10 p-6">
                  <h2 className="text-xl font-semibold text-white mb-6">Create Your Account</h2>
                  
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="fullName" className="text-white">Full Name</Label>
                        <Input
                          id="fullName"
                          name="fullName"
                          value={formData.fullName}
                          onChange={handleInputChange}
                          placeholder="John Doe"
                          required
                          className="bg-white/5 border-white/10 text-white"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="companyName" className="text-white">Company Name</Label>
                        <Input
                          id="companyName"
                          name="companyName"
                          value={formData.companyName}
                          onChange={handleInputChange}
                          placeholder="Your Company"
                          required
                          className="bg-white/5 border-white/10 text-white"
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-white">Email</Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        placeholder="you@example.com"
                        required
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="password" className="text-white">Password</Label>
                      <Input
                        id="password"
                        name="password"
                        type="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        placeholder="••••••••"
                        required
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>
                    
                    <div className="pt-4 flex justify-between items-center">
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={() => setStep(1)}
                        className="text-white border-white/20 bg-white/5 hover:bg-white/10"
                      >
                        Back
                      </Button>
                      <Button 
                        type="submit" 
                        className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90"
                        disabled={isLoading}
                      >
                        {isLoading ? "Creating Account..." : "Create Account"}
                      </Button>
                    </div>
                  </form>
                  
                  <div className="mt-6 text-center">
                    <p className="text-white/70 text-sm">
                      Already have an account?{" "}
                      <Link href="/login" className="text-[#6ACBDF] hover:underline">
                        Log in
                      </Link>
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
