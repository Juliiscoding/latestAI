import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { extractTenantFromHostname } from "./lib/tenant/context"
import { verifyToken, JwtPayload } from "./lib/auth/utils"

export function middleware(request: NextRequest) {
  // Multi-Tenant Identifikation - Tenant aus Hostname oder URL-Pfad extrahieren
  const hostname = request.headers.get('host') || ''
  let tenantSlug = extractTenantFromHostname(hostname)
  
  // Alternative: Tenant aus URL-Pfad extrahieren (z.B. /tenant/tenant-slug/...)
  if (!tenantSlug && request.nextUrl.pathname.startsWith('/tenant/')) {
    const pathSegments = request.nextUrl.pathname.split('/')
    if (pathSegments.length > 2) {
      tenantSlug = pathSegments[2]
    }
  }
  
  // Check if we're in a preview or development environment
  const isPreview = 
    process.env.NEXT_PUBLIC_VERCEL_ENV === 'preview' || 
    process.env.NODE_ENV === 'development' ||
    hostname.includes('localhost') ||
    hostname.includes('127.0.0.1') ||
    hostname.includes('vercel.app') ||
    hostname.includes('55698')

  // Paths that don't require authentication
  const publicPaths = ["/", "/login", "/signup", "/api/login", "/api/logout", "/favicon.ico", "/features", "/how-it-works", "/examples", "/pricing", "/legal/impressum", "/legal/datenschutz", "/legal/agb", "/legal/cookie-policy", "/legal/widerrufsrecht", "/about", "/contact"]
  const isPublicPath = publicPaths.some(path => request.nextUrl.pathname === path) ||
    request.nextUrl.pathname.startsWith('/_next/') ||
    request.nextUrl.pathname.startsWith('/public/') ||
    request.nextUrl.pathname.startsWith('/api/tenant/public')

  // Admin-Pfade erfordern besondere Berechtigungen
  const isAdminPath = request.nextUrl.pathname.startsWith('/admin')
  
  // Prüfe den Auth-Token (JWT) statt eines einfachen Cookies
  const authToken = request.cookies.get("mercurios_auth")?.value
  let tokenPayload: JwtPayload | null = null
  
  if (authToken) {
    tokenPayload = verifyToken(authToken)
  }

  // Für öffentliche Pfade keinen Auth-Check durchführen
  if (isPublicPath) {
    const response = NextResponse.next()
    // Wenn Tenant-Kontext vorhanden ist, setzen wir ihn in den Response-Header
    if (tenantSlug) {
      response.headers.set('x-tenant-slug', tenantSlug)
    }
    return response
  }

  // In Preview-Umgebungen temporären Zugang gewähren
  if (isPreview) {
    if (!authToken) {
      // Redirect zum Login für bessere Test-Erfahrung in der Preview
      if (isAdminPath) {
        return NextResponse.redirect(new URL("/admin/login", request.url))
      }
      return NextResponse.redirect(new URL("/login", request.url))
    }
    const response = NextResponse.next()
    if (tenantSlug) {
      response.headers.set('x-tenant-slug', tenantSlug)
    }
    return response
  }

  // In Produktion vollständigen Auth-Check durchführen
  if (!tokenPayload) {
    if (isAdminPath) {
      return NextResponse.redirect(new URL("/admin/login", request.url))
    }
    return NextResponse.redirect(new URL("/login", request.url))
  }
  
  // Admin-Zugriffskontrolle: Nur Admin-Rolle darf auf Admin-Bereich zugreifen
  if (isAdminPath && tokenPayload.role !== 'ADMIN') {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }
  
  // Tenant-spezifische Zugriffskontrolle
  if (tenantSlug && tokenPayload.tenantId) {
    // Hier könnten wir prüfen, ob der Benutzer Zugriff auf diesen Tenant hat
    // Für jetzt überspringen wir diese Prüfung, da wir sie in den API-Routen implementieren werden
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
}

