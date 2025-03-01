import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { LoginForm } from "@/components/login-form"
import { StarField } from "@/components/star-field"
import { SparklesCore } from "@/components/sparkles"

export default function LoginPage() {
  // Check if user is already authenticated
  const cookieStore = cookies()
  const isAuthenticated = cookieStore.get("auth")?.value === "true"

  // If authenticated, redirect to dashboard
  if (isAuthenticated) {
    redirect("/dashboard")
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-black">
      {/* Background Effects */}
      <StarField />
      <div className="absolute inset-0 z-[1] opacity-50">
        <SparklesCore
          id="tsparticleslogin"
          background="transparent"
          minSize={0.2}
          maxSize={0.6}
          particleDensity={100}
          className="h-full w-full"
          particleColor="#FFFFFF"
        />
      </div>

      {/* Login Form */}
      <div className="relative z-10 flex min-h-screen flex-col items-center justify-center p-4">
        <div className="w-full max-w-md">
          <LoginForm />
        </div>
      </div>
    </div>
  )
}

