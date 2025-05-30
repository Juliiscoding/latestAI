// app/api/admin/users/route.ts
import { NextResponse } from 'next/server';
import prisma from '@/lib/db';
import { getCurrentUser, hashPassword } from '@/lib/auth/utils';

// GET /api/admin/users - Liste aller Benutzer abrufen
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
    const tenantId = searchParams.get('tenantId') || undefined;
    const sortParam = searchParams.get('sort') || 'createdAt:desc';
    
    // Sortierung parsen
    const [sortField, sortDirection] = sortParam.split(':');
    const orderBy: any = {};
    orderBy[sortField || 'createdAt'] = sortDirection === 'asc' ? 'asc' : 'desc';
    
    // Filter aufbauen
    const whereClause: any = {
      OR: [
        { email: { contains: search, mode: 'insensitive' } },
        { name: { contains: search, mode: 'insensitive' } }
      ]
    };
    
    if (tenantId) {
      whereClause.tenantId = tenantId;
    }
    
    // Benutzer abfragen
    const [users, total] = await Promise.all([
      prisma.user.findMany({
        where: whereClause,
        orderBy,
        take: limit,
        skip: offset,
        include: {
          tenant: {
            select: {
              name: true,
              slug: true
            }
          }
        }
      }),
      prisma.user.count({
        where: whereClause
      })
    ]);
    
    // Passwörter aus den Ergebnissen entfernen
    const sanitizedUsers = users.map(user => {
      const { password, ...userWithoutPassword } = user;
      return userWithoutPassword;
    });
    
    // Ergebnisse zurückgeben
    return NextResponse.json({
      users: sanitizedUsers,
      total,
      limit,
      offset
    });
    
  } catch (error) {
    console.error('Error fetching users:', error);
    return NextResponse.json(
      { error: 'Ein Fehler ist aufgetreten beim Laden der Benutzer.' },
      { status: 500 }
    );
  }
}

// POST /api/admin/users - Neuen Benutzer erstellen
export async function POST(request: Request) {
  try {
    // Überprüfen, ob der Benutzer ein Administrator ist
    const currentUser = await getCurrentUser();
    
    if (!currentUser || currentUser.role !== 'ADMIN') {
      return NextResponse.json(
        { error: 'Zugriff verweigert. Nur Administratoren können neue Benutzer erstellen.' },
        { status: 403 }
      );
    }
    
    // Daten aus dem Request-Body extrahieren
    const data = await request.json();
    const { email, name, password, tenantId, role } = data;
    
    // Validierung
    if (!email || !password || !tenantId) {
      return NextResponse.json(
        { error: 'Email, Passwort und Tenant-ID sind erforderlich.' },
        { status: 400 }
      );
    }
    
    // Prüfen, ob die E-Mail bereits existiert
    const existingUser = await prisma.user.findUnique({
      where: { email }
    });
    
    if (existingUser) {
      return NextResponse.json(
        { error: 'Ein Benutzer mit dieser E-Mail existiert bereits.' },
        { status: 409 }
      );
    }
    
    // Prüfen, ob der angegebene Tenant existiert
    const tenant = await prisma.tenant.findUnique({
      where: { id: tenantId }
    });
    
    if (!tenant) {
      return NextResponse.json(
        { error: 'Der angegebene Tenant existiert nicht.' },
        { status: 400 }
      );
    }
    
    // Passwort hashen
    const hashedPassword = await hashPassword(password);
    
    // Neuen Benutzer erstellen
    const newUser = await prisma.user.create({
      data: {
        email,
        name,
        password: hashedPassword,
        tenantId,
        role: role || 'USER'
      }
    });
    
    // Aktivität protokollieren
    await prisma.activity.create({
      data: {
        userId: currentUser.id,
        tenantId: tenant.id,
        action: 'USER_CREATED',
        details: { email, name, tenantId, role }
      }
    });
    
    // Passwort aus dem Ergebnis entfernen
    const { password: _, ...userWithoutPassword } = newUser;
    
    // Ergebnis zurückgeben
    return NextResponse.json(userWithoutPassword, { status: 201 });
    
  } catch (error) {
    console.error('Error creating user:', error);
    return NextResponse.json(
      { error: 'Ein Fehler ist aufgetreten beim Erstellen des Benutzers.' },
      { status: 500 }
    );
  }
}
