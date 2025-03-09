import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  // Check for auth cookie
  const authCookie = request.cookies.get("auth")?.value
  
  // Check if we're in a preview or development environment
  const hostname = request.headers.get('host') || ''
  const isPreview = 
    process.env.NEXT_PUBLIC_VERCEL_ENV === 'preview' || 
    process.env.NODE_ENV === 'development' ||
    hostname.includes('localhost') ||
    hostname.includes('127.0.0.1') ||
    hostname.includes('vercel.app') ||
    hostname.includes('55698')

  // Paths that don't require authentication
  const publicPaths = ["/", "/login", "/signup", "/api/login", "/api/logout", "/favicon.ico"]
  const isPublicPath = publicPaths.some(path => request.nextUrl.pathname === path) ||
    request.nextUrl.pathname.startsWith('/_next/') ||
    request.nextUrl.pathname.startsWith('/public/')

  if (isPublicPath) {
    return NextResponse.next()
  }

  // In preview/development mode, always bypass authentication for testing
  if (isPreview) {
    // If not authenticated in preview, set a temporary auth cookie
    if (!authCookie) {
      const response = NextResponse.next()
      response.cookies.set("auth", "true", {
        path: '/',
        maxAge: 60 * 60 * 24, // 1 day
      })
      return response
    }
    return NextResponse.next()
  }

  // In production, check if user is authenticated
  if (!authCookie) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
}

