// app/api/admin/stats/route.ts
import { NextResponse } from 'next/server';
import prisma from '@/lib/db';
import { getCurrentUser } from '@/lib/auth/utils';

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

    // Aktuelle Datum für Abfragen
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    // Statistiken berechnen
    const [
      totalTenants,
      totalUsers,
      activeUsers,
      newUsersToday,
      loginCount24h
    ] = await Promise.all([
      // Gesamtzahl der Tenants
      prisma.tenant.count(),
      
      // Gesamtzahl der Benutzer
      prisma.user.count(),
      
      // Aktive Benutzer (mindestens ein Login in den letzten 30 Tagen)
      prisma.user.count({
        where: {
          lastLogin: {
            gte: new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000) // 30 Tage zurück
          }
        }
      }),
      
      // Neue Benutzer heute
      prisma.user.count({
        where: {
          createdAt: {
            gte: new Date(today.setHours(0, 0, 0, 0)) // Heute um Mitternacht
          }
        }
      }),
      
      // Login-Versuche in den letzten 24 Stunden
      prisma.loginHistory.count({
        where: {
          timestamp: {
            gte: yesterday
          },
          success: true
        }
      })
    ]);
    
    // Statistiken zurückgeben
    return NextResponse.json({
      totalTenants,
      totalUsers,
      activeUsers,
      newUsersToday,
      loginCount24h
    });
    
  } catch (error) {
    console.error('Error fetching admin stats:', error);
    return NextResponse.json(
      { error: 'Ein Fehler ist aufgetreten beim Laden der Statistiken.' },
      { status: 500 }
    );
  }
}
