import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const authCookie = request.cookies.get("auth")?.value

  // Paths that don't require authentication
  const publicPaths = ["/", "/login", "/signup", "/api/login"]
  if (publicPaths.some((path) => request.nextUrl.pathname === path)) {
    return NextResponse.next()
  }

  // Check if user is authenticated
  if (!authCookie) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
}

