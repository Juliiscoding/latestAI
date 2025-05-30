// app/api/admin/login/route.ts
import { NextResponse } from 'next/server';
import prisma from '@/lib/db';
import { loginUser, setAuthCookie } from '@/lib/auth/utils';

export async function POST(request: Request) {
  try {
    const { email, password } = await request.json();

    // Benutzerdaten validieren
    if (!email || !password) {
      return NextResponse.json(
        { success: false, message: 'Email und Passwort sind erforderlich' },
        { status: 400 }
      );
    }

    // Benutzer authentifizieren
    const ipAddress = request.headers.get('x-forwarded-for') || 'unknown';
    const userAgent = request.headers.get('user-agent') || 'unknown';
    
    const result = await loginUser(email, password, ipAddress, userAgent);
    
    if (!result) {
      return NextResponse.json(
        { success: false, message: 'Ungültige Anmeldedaten' },
        { status: 401 }
      );
    }

    const { user, token } = result;

    // Überprüfen, ob der Benutzer ein Administrator ist
    if (user.role !== 'ADMIN') {
      return NextResponse.json(
        { success: false, message: 'Zugriff verweigert. Nur Administratoren haben Zugriff auf diesen Bereich.' },
        { status: 403 }
      );
    }

    // Erfolgreiche Anmeldung: JWT-Token im Cookie setzen
    const response = NextResponse.json(
      { success: true, user: { id: user.id, email: user.email, role: user.role } },
      { status: 200 }
    );

    setAuthCookie(response, token);

    return response;
  } catch (error) {
    console.error('Admin login error:', error);
    return NextResponse.json(
      { success: false, message: 'Ein Fehler ist aufgetreten' },
      { status: 500 }
    );
  }
}
