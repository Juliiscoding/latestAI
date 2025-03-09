import { NextResponse } from "next/server"

export async function GET(request: Request) {
  // Create a response that will clear the auth cookie
  const response = NextResponse.json({ success: true })
  
  // Clear the auth cookie
  response.cookies.set("auth", "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 0, // Expire immediately
    path: '/',
  })
  
  return response
}
