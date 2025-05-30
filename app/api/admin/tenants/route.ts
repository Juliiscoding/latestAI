// app/api/admin/tenants/route.ts
import { NextResponse } from 'next/server';
import prisma from '@/lib/db';
import { getCurrentUser } from '@/lib/auth/utils';

// GET /api/admin/tenants - Liste aller Tenants abrufen
export async function GET(request: Request) {
  try {
    // Überprüfen, ob der Benutzer ein Administrator ist
    const currentUser = await getCurrentUser();
    
    if (!currentUser || currentUser.role !== 'ADMIN') {
      return NextResponse.json(
        { error: 'Zugriff verweigert. Nur Administratoren haben Zugriff auf diese Daten.' },
        { status: 403 }
      );
    }
    
    // URL-Parameter extrahieren
    const { searchParams } = new URL(request.url);
    const limit = Number(searchParams.get('limit')) || 100;
    const offset = Number(searchParams.get('offset')) || 0;
    const search = searchParams.get('search') || '';
    
    // Tenants abfragen
    const [tenants, total] = await Promise.all([
      prisma.tenant.findMany({
        where: {
          OR: [
            { name: { contains: search, mode: 'insensitive' } },
            { slug: { contains: search, mode: 'insensitive' } }
          ]
        },
        orderBy: { createdAt: 'desc' },
        take: limit,
        skip: offset,
      }),
      prisma.tenant.count({
        where: {
          OR: [
            { name: { contains: search, mode: 'insensitive' } },
            { slug: { contains: search, mode: 'insensitive' } }
          ]
        }
      })
    ]);
    
    // Ergebnisse zurückgeben
    return NextResponse.json({
      tenants,
      total,
      limit,
      offset
    });
    
  } catch (error) {
    console.error('Error fetching tenants:', error);
    return NextResponse.json(
      { error: 'Ein Fehler ist aufgetreten beim Laden der Tenants.' },
      { status: 500 }
    );
  }
}

// POST /api/admin/tenants - Neuen Tenant erstellen
export async function POST(request: Request) {
  try {
    // Überprüfen, ob der Benutzer ein Administrator ist
    const currentUser = await getCurrentUser();
    
    if (!currentUser || currentUser.role !== 'ADMIN') {
      return NextResponse.json(
        { error: 'Zugriff verweigert. Nur Administratoren können neue Tenants erstellen.' },
        { status: 403 }
      );
    }
    
    // Daten aus dem Request-Body extrahieren
    const data = await request.json();
    const { name, slug, settings, dataSourceConfig } = data;
    
    // Validierung
    if (!name || !slug) {
      return NextResponse.json(
        { error: 'Name und Slug sind erforderlich.' },
        { status: 400 }
      );
    }
    
    // Prüfen, ob der Slug bereits existiert
    const existingTenant = await prisma.tenant.findUnique({
      where: { slug }
    });
    
    if (existingTenant) {
      return NextResponse.json(
        { error: 'Ein Tenant mit diesem Slug existiert bereits.' },
        { status: 409 }
      );
    }
    
    // Neuen Tenant erstellen
    const newTenant = await prisma.tenant.create({
      data: {
        name,
        slug,
        settings: settings || {},
        dataSourceConfig: dataSourceConfig || {}
      }
    });
    
    // Aktivität protokollieren
    await prisma.activity.create({
      data: {
        userId: currentUser.id,
        tenantId: newTenant.id,
        action: 'TENANT_CREATED',
        details: { name, slug }
      }
    });
    
    // Ergebnis zurückgeben
    return NextResponse.json(newTenant, { status: 201 });
    
  } catch (error) {
    console.error('Error creating tenant:', error);
    return NextResponse.json(
      { error: 'Ein Fehler ist aufgetreten beim Erstellen des Tenants.' },
      { status: 500 }
    );
  }
}
