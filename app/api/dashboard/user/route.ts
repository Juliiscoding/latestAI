// app/api/dashboard/user/route.ts
import { NextRequest, NextResponse } from 'next/server';
import prisma from '@/lib/db';
import { getCurrentUser } from '@/lib/auth/utils';

export async function GET(request: NextRequest) {
  try {
    // Aktuellen Benutzer ermitteln
    const currentUser = await getCurrentUser(request);
    
    // Prüfen, ob der Benutzer authentifiziert ist
    if (!currentUser) {
      return NextResponse.json(
        { error: 'Nicht authentifiziert' },
        { status: 401 }
      );
    }
    
    // Tenant-ID aus Query-Parameter oder vom Benutzer
    let tenantId = request.nextUrl.searchParams.get('tenantId') || currentUser.tenantId;
    
    // Wenn der Benutzer kein Admin ist, darf er nur seinen eigenen Tenant sehen
    if (currentUser.role !== 'ADMIN' && tenantId !== currentUser.tenantId) {
      return NextResponse.json(
        { error: 'Zugriff verweigert' },
        { status: 403 }
      );
    }
    
    // Benutzer mit Login-Historie laden
    const user = await prisma.user.findUnique({
      where: { id: currentUser.id },
      include: {
        loginHistory: {
          orderBy: { createdAt: 'desc' },
          take: 5,
        },
        activities: {
          orderBy: { createdAt: 'desc' },
          take: 10,
        },
      },
    });
    
    if (!user) {
      return NextResponse.json(
        { error: 'Benutzer nicht gefunden' },
        { status: 404 }
      );
    }
    
    // Benutzerdaten ohne sensible Informationen zurückgeben
    const userData = {
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
        avatar: user.avatar,
        createdAt: user.createdAt,
        lastLogin: user.loginHistory[0]?.createdAt || null,
      },
      recentLogins: user.loginHistory.map(login => ({
        id: login.id,
        date: login.createdAt,
        ipAddress: login.ipAddress,
        userAgent: login.userAgent,
        success: login.success,
      })),
      recentActivities: user.activities.map(activity => ({
        id: activity.id,
        type: activity.type,
        description: activity.description,
        date: activity.createdAt,
      })),
    };
    
    return NextResponse.json(userData);
  } catch (error) {
    console.error('Error fetching user data:', error);
    return NextResponse.json(
      { error: 'Ein Fehler ist aufgetreten' },
      { status: 500 }
    );
  }
}
