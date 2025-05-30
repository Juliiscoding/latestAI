"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { StarField } from "@/components/star-field"
import { SparklesCore } from "@/components/sparkles"

export default function AdminLoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    
    try {
      const response = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })

      const data = await response.json()
      
      if (response.ok) {
        // Erfolgreich eingeloggt, weiterleiten zum Admin-Dashboard
        router.push("/admin/dashboard")
      } else {
        setError(data.message || "Login fehlgeschlagen. Nur Administratoren haben Zugriff.")
      }
    } catch (error) {
      console.error("Login error:", error)
      setError("Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.")
    }
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-black">
      {/* Background Effects */}
      <StarField />
      <div className="absolute inset-0 z-[1] opacity-50">
        <SparklesCore
          id="tsparticlesadmin"
          background="transparent"
          minSize={0.2}
          maxSize={0.6}
          particleDensity={100}
          className="h-full w-full"
          particleColor="#FFFFFF"
        />
      </div>

      {/* Admin Login Form */}
      <div className="relative z-10 flex min-h-screen flex-col items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Card className="border-none bg-white/95 shadow-lg backdrop-blur-sm">
            <CardContent className="p-4 sm:p-6">
              <div className="flex flex-col gap-4 sm:gap-6">
                <div className="flex flex-col items-center gap-2 text-center">
                  <h1 className="text-xl sm:text-2xl font-bold tracking-tight">Admin-Bereich</h1>
                  <p className="text-xs sm:text-sm text-muted-foreground">
                    Anmeldung für Mercurios.ai Administratoren
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                  {error && <p className="text-xs sm:text-sm text-red-500 text-center">{error}</p>}

                  <div className="grid gap-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="admin@mercurios.ai"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="password">Passwort</Label>
                    <Input
                      id="password"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>

                  <Button type="submit" className="w-full bg-[#6ACBDF] text-white hover:bg-[#6ACBDF]/90">
                    Admin Login
                  </Button>
                </form>

                <div className="text-center text-xs sm:text-sm">
                  <Link href="/" className="text-[#6ACBDF] hover:text-[#6ACBDF]/90">
                    Zurück zur Startseite
                  </Link>
                </div>

                <div className="text-center text-xs text-muted-foreground">
                  Der Admin-Bereich ist nur für autorisierte Mitarbeiter zugänglich.
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
