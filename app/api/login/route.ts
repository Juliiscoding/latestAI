import { NextResponse } from "next/server"

export async function POST(request: Request) {
  const { email, password } = await request.json()

  // Valid credentials array
  const validCredentials = [
    { email: "m@example.com", password: "password123" },
    { email: "demo@mercurios.ai", password: "demo123" },
    // Test account matching the placeholder in the login form
    { email: "m@example.com", password: "password" },
    { email: "julius@mercurios.ai", password: "password" }, // Added new credential
  ]

  // Check if the provided credentials match any valid pair
  const isValid = validCredentials.some((cred) => cred.email === email && cred.password === password)

  if (isValid) {
    const response = NextResponse.json({ success: true })
    // Set auth cookie
    response.cookies.set("auth", "true", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 1 week
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

