import Hero from "@/components/hero"
import Navbar from "@/components/navbar"
import { SparklesCore } from "@/components/sparkles"
import { StarField } from "@/components/star-field"

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-black antialiased relative overflow-hidden">
      {/* Star field animation */}
      <StarField />

      {/* Ambient background with moving particles */}
      <div className="h-full w-full absolute inset-0 z-[1] opacity-50">
        <SparklesCore
          id="tsparticlesfullpage"
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
        <Hero />
      </div>
    </main>
  )
}

