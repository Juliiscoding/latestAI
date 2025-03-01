import { NextResponse } from "next/server"
import { cookies } from "next/headers"

export async function GET() {
  const cookieStore = cookies()
  const sessionCookie = cookieStore.get("session")
  const isAuthenticated = sessionCookie?.value === "authenticated"

  return NextResponse.json({ authenticated: isAuthenticated })
}

