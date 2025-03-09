import { NextResponse } from "next/server"

export async function POST(request: Request) {
  const { email, password } = await request.json()

  // Valid credentials array - accept any credentials in preview for testing
  const validCredentials = [
    { email: "m@example.com", password: "password123" },
    { email: "demo@mercurios.ai", password: "demo123" },
    // Test account matching the placeholder in the login form
    { email: "m@example.com", password: "password" },
    { email: "julius@mercurios.ai", password: "password" }, // Added new credential
  ]

  // In preview/development, accept any non-empty credentials for testing
  const isPreview = process.env.NEXT_PUBLIC_VERCEL_ENV === 'preview' || process.env.NODE_ENV === 'development';
  
  // Check if the provided credentials match any valid pair or if we're in preview mode
  const isValid = isPreview ? (email && password) : 
    validCredentials.some((cred) => cred.email === email && cred.password === password)

  if (isValid) {
    const response = NextResponse.json({ success: true })
    // Set auth cookie
    response.cookies.set("auth", "true", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 1 week
      path: '/',
    })
    return response
  }

  return NextResponse.json(
    {
      success: false,
      message: "Invalid email or password",
    },
    { status: 401 },
  )
}

