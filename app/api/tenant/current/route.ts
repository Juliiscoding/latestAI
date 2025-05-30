// app/api/tenant/current/route.ts
import { NextRequest, NextResponse } from 'next/server';
import prisma from '@/lib/db';
import { getCurrentUser } from '@/lib/auth/utils';

export async function GET(request: NextRequest) {
  try {
    // Tenant aus Header oder URL-Parameter holen
    const tenantSlug = request.headers.get('x-tenant-slug') || request.nextUrl.searchParams.get('slug');
    
    // Versuche, den aktuellen Benutzer zu ermitteln
    const currentUser = await getCurrentUser(request);
    
    // Wenn ein Tenant-Slug angegeben wurde, suche diesen Tenant
    if (tenantSlug) {
      const tenant = await prisma.tenant.findUnique({
        where: { slug: tenantSlug },
      });
      
      // Wenn der Tenant gefunden wurde und der Benutzer authentifiziert ist,
      // prüfe, ob der Benutzer Zugriff auf diesen Tenant hat
      if (tenant && currentUser) {
        // Admin hat Zugriff auf alle Tenants
        if (currentUser.role === 'ADMIN') {
          return NextResponse.json({ tenant });
        }
        
        // Normale Benutzer haben nur Zugriff auf ihren eigenen Tenant
        if (currentUser.tenantId === tenant.id) {
          return NextResponse.json({ tenant });
        }
        
        // Wenn der Benutzer keinen Zugriff hat, gib einen Fehler zurück
        return NextResponse.json(
          { error: 'Sie haben keinen Zugriff auf diesen Tenant.' },
          { status: 403 }
        );
      }
      
      // Wenn der Tenant nicht gefunden wurde, gib einen Fehler zurück
      if (!tenant) {
        return NextResponse.json(
          { error: 'Tenant nicht gefunden.' },
          { status: 404 }
        );
      }
    }
    
    // Wenn kein Tenant-Slug angegeben wurde, aber ein Benutzer authentifiziert ist,
    // gib den Tenant des Benutzers zurück
    if (currentUser) {
      const tenant = await prisma.tenant.findUnique({
        where: { id: currentUser.tenantId },
      });
      
      if (tenant) {
        return NextResponse.json({ tenant });
      }
    }
    
    // Wenn kein Tenant gefunden wurde oder der Benutzer nicht authentifiziert ist,
    // gib null zurück
    return NextResponse.json({ tenant: null });
  } catch (error) {
    console.error('Error fetching tenant:', error);
    return NextResponse.json(
      { error: 'Ein Fehler ist aufgetreten.' },
      { status: 500 }
    );
  }
}
