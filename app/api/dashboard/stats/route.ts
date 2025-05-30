// app/api/dashboard/stats/route.ts
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
    const tenantId = request.nextUrl.searchParams.get('tenantId') || currentUser.tenantId;
    
    // Wenn der Benutzer kein Admin ist, darf er nur seinen eigenen Tenant sehen
    if (currentUser.role !== 'ADMIN' && tenantId !== currentUser.tenantId) {
      return NextResponse.json(
        { error: 'Zugriff verweigert' },
        { status: 403 }
      );
    }
    
    // Prüfen, ob der Tenant existiert
    const tenant = await prisma.tenant.findUnique({
      where: { id: tenantId as string },
    });
    
    if (!tenant) {
      return NextResponse.json(
        { error: 'Tenant nicht gefunden' },
        { status: 404 }
      );
    }
    
    // Statistiken berechnen
    
    // 1. Gesamtzahl der Benutzer im Tenant
    const totalUsers = await prisma.user.count({
      where: { tenantId: tenantId as string },
    });
    
    // 2. Aktive Benutzer (Anmeldung in den letzten 30 Tagen)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    const activeUsers = await prisma.user.count({
      where: {
        tenantId: tenantId as string,
        loginHistory: {
          some: {
            createdAt: { gte: thirtyDaysAgo },
            success: true,
          },
        },
      },
    });
    
    // 3. Neue Registrierungen in den letzten 30 Tagen
    const newSignups = await prisma.user.count({
      where: {
        tenantId: tenantId as string,
        createdAt: { gte: thirtyDaysAgo },
      },
    });
    
    // 4. Retention Rate (Vereinfacht: Prozent der Benutzer, die sich in den letzten 30 Tagen angemeldet haben)
    const retention = totalUsers > 0 ? Math.round((activeUsers / totalUsers) * 100) : 0;
    
    // 5. Wachstumsraten berechnen (Vergleich mit den vorherigen 30 Tagen)
    const sixtyDaysAgo = new Date();
    sixtyDaysAgo.setDate(sixtyDaysAgo.getDate() - 60);
    
    // Benutzer vor 30-60 Tagen
    const previousTotalUsers = await prisma.user.count({
      where: {
        tenantId: tenantId as string,
        createdAt: { lte: thirtyDaysAgo },
      },
    });
    
    // Aktive Benutzer vor 30-60 Tagen
    const previousActiveUsers = await prisma.user.count({
      where: {
        tenantId: tenantId as string,
        loginHistory: {
          some: {
            createdAt: { gte: sixtyDaysAgo, lte: thirtyDaysAgo },
            success: true,
          },
        },
      },
    });
    
    // Neue Registrierungen vor 30-60 Tagen
    const previousNewSignups = await prisma.user.count({
      where: {
        tenantId: tenantId as string,
        createdAt: { gte: sixtyDaysAgo, lte: thirtyDaysAgo },
      },
    });
    
    // Retention vor 30-60 Tagen
    const previousRetention = previousTotalUsers > 0 
      ? Math.round((previousActiveUsers / previousTotalUsers) * 100) 
      : 0;
    
    // Wachstumsraten berechnen (prozentual)
    const calculateGrowth = (current: number, previous: number) => {
      if (previous === 0) return current > 0 ? "+100" : "0";
      const growth = Math.round(((current - previous) / previous) * 100);
      return growth >= 0 ? `+${growth}` : `${growth}`;
    };
    
    const totalGrowth = calculateGrowth(totalUsers, previousTotalUsers);
    const activeGrowth = calculateGrowth(activeUsers, previousActiveUsers);
    const newGrowth = calculateGrowth(newSignups, previousNewSignups);
    const retentionGrowth = calculateGrowth(retention, previousRetention);
    
    return NextResponse.json({
      totalUsers,
      activeUsers,
      newSignups,
      retention,
      totalGrowth,
      activeGrowth,
      newGrowth,
      retentionGrowth,
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    return NextResponse.json(
      { error: 'Ein Fehler ist aufgetreten' },
      { status: 500 }
    );
  }
}
