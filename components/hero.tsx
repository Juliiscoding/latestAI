import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function Hero() {
  return (
    <div className="container flex min-h-[calc(100vh-3.5rem)] items-center">
      <div className="relative z-10 mx-auto w-full max-w-4xl text-center">
        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-mono font-bold text-white">
          Transform Your Business with{" "}
          <span className="bg-gradient-to-r from-[#6ACBDF] to-[#AA0E33] bg-clip-text text-transparent">
            AI-Powered Analytics
          </span>
        </h1>
        <p className="mx-auto mt-4 sm:mt-6 max-w-2xl text-sm sm:text-base md:text-lg text-white/60 uppercase tracking-wide">
          HARNESS THE POWER OF AI TO GAIN UNPRECEDENTED INSIGHTS INTO YOUR BUSINESS DATA, MAKE INFORMED DECISIONS, AND
          STAY AHEAD OF THE COMPETITION.
        </p>
        <div className="mt-6 sm:mt-8 flex flex-wrap justify-center gap-4">
          <Link href="/signup">
            <Button size="lg" className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">
              Start Analyzing
            </Button>
          </Link>
          <Link href="/demo">
            <Button size="lg" variant="outline" className="text-white border-white/20 bg-white/5 hover:bg-white/10">
              See Demo
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}

