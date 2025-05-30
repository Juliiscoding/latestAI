// lib/auth/utils.ts
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';
import prisma from '../db';
import { User, Role } from '@prisma/client';

// Konstanten
const JWT_SECRET = process.env.JWT_SECRET || 'fallback-jwt-secret-for-dev';
const TOKEN_EXPIRY = '24h';
const COOKIE_NAME = 'mercurios_auth';

// Typen
export interface JwtPayload {
  userId: string;
  email: string;
  tenantId: string;
  role: Role;
}

// Passwort-Hashing
export async function hashPassword(password: string): Promise<string> {
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(password, salt);
}

export async function verifyPassword(plain: string, hashed: string): Promise<boolean> {
  return bcrypt.compare(plain, hashed);
}

// JWT-Funktionen
export function generateToken(user: User): string {
  const payload: JwtPayload = {
    userId: user.id,
    email: user.email,
    tenantId: user.tenantId,
    role: user.role
  };
  return jwt.sign(payload, JWT_SECRET, { expiresIn: TOKEN_EXPIRY });
}

export function verifyToken(token: string): JwtPayload | null {
  try {
    return jwt.verify(token, JWT_SECRET) as JwtPayload;
  } catch (error) {
    return null;
  }
}

// Cookie-Management
export function setAuthCookie(response: NextResponse, token: string) {
  // Secure HTTP-only Cookie
  response.cookies.set({
    name: COOKIE_NAME,
    value: token,
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24, // 24 Stunden
    path: '/'
  });
  return response;
}

export function getAuthCookie(): string | undefined {
  const cookieStore = cookies();
  return cookieStore.get(COOKIE_NAME)?.value;
}

export function removeAuthCookie(response: NextResponse) {
  response.cookies.delete(COOKIE_NAME);
  return response;
}

// Authentifizierungs-Hilfsfunktionen
export async function getUserFromToken(token: string | undefined): Promise<User | null> {
  if (!token) return null;
  
  const payload = verifyToken(token);
  if (!payload) return null;
  
  try {
    return await prisma.user.findUnique({
      where: { id: payload.userId },
      include: { tenant: true }
    });
  } catch (error) {
    console.error('Error fetching user from token:', error);
    return null;
  }
}

export async function getCurrentUser(req?: NextRequest): Promise<User | null> {
  const token = req ? req.cookies.get(COOKIE_NAME)?.value : getAuthCookie();
  return getUserFromToken(token);
}

// Login-Funktion
export async function loginUser(email: string, password: string, ipAddress?: string, userAgent?: string): Promise<{ user: User; token: string } | null> {
  try {
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user || !user.password) return null;
    
    const isValid = await verifyPassword(password, user.password);
    if (!isValid) {
      // Fehlgeschlagenen Login-Versuch protokollieren
      await prisma.loginHistory.create({
        data: {
          userId: user.id,
          ipAddress,
          userAgent,
          success: false
        }
      });
      return null;
    }
    
    // Erfolgreichen Login protokollieren
    await prisma.loginHistory.create({
      data: {
        userId: user.id,
        ipAddress,
        userAgent,
        success: true
      }
    });
    
    // User-Status aktualisieren
    await prisma.user.update({
      where: { id: user.id },
      data: { lastLogin: new Date() }
    });
    
    const token = generateToken(user);
    return { user, token };
  } catch (error) {
    console.error('Login error:', error);
    return null;
  }
}

// Aktivität protokollieren
export async function logActivity(userId: string, tenantId: string, action: string, details?: any) {
  try {
    return await prisma.activity.create({
      data: {
        userId,
        tenantId,
        action,
        details: details ? JSON.stringify(details) : null
      }
    });
  } catch (error) {
    console.error('Error logging activity:', error);
  }
}
