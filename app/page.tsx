import Hero from "@/components/hero"
import Navbar from "@/components/navbar"
import { SplashCursor } from "@/components/ui/splash-cursor"

export default function LandingPage() {
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
        <Hero />
      </div>
    </main>
  )
}

