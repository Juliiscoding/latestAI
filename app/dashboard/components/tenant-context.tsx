"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

// Tenant-Typ für typsichere Verwendung
export interface TenantData {
  id: string;
  name: string;
  slug: string;
  settings: any;
  dataSourceConfig: any;
}

// Kontext-Typ-Definition
interface TenantContextType {
  tenant: TenantData | null;
  isLoading: boolean;
  error: string | null;
}

// Erstellen des Kontexts mit Standardwerten
const TenantContext = createContext<TenantContextType>({
  tenant: null,
  isLoading: true,
  error: null
});

// Hook für einfachen Zugriff auf den Tenant-Kontext
export const useTenantContext = () => useContext(TenantContext);

// Provider-Komponente für den Tenant-Kontext
export function TenantProvider({ children }: { children: React.ReactNode }) {
  const [tenant, setTenant] = useState<TenantData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Beim Komponenten-Mount den aktuellen Tenant laden
  useEffect(() => {
    async function loadTenant() {
      try {
        setIsLoading(true);
        const response = await fetch('/api/tenant/current');
        
        if (!response.ok) {
          // Bei HTTP-Fehlern zum Login umleiten
          if (response.status === 401 || response.status === 403) {
            router.push('/login');
            return;
          }
          throw new Error(`Fehler beim Laden des Tenants: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.tenant) {
          throw new Error('Kein Tenant gefunden');
        }
        
        setTenant(data.tenant);
        setError(null);
      } catch (err: any) {
        console.error('Fehler beim Laden des Tenants:', err);
        setError(err.message || 'Ein unbekannter Fehler ist aufgetreten');
      } finally {
        setIsLoading(false);
      }
    }
    
    loadTenant();
  }, [router]);

  // Werte, die über den Kontext bereitgestellt werden
  const contextValue = {
    tenant,
    isLoading,
    error
  };

  return (
    <TenantContext.Provider value={contextValue}>
      {children}
    </TenantContext.Provider>
  );
}

// HOC (Higher Order Component) um Komponenten mit dem Tenant-Kontext zu umschließen
export function withTenantContext<P extends object>(Component: React.ComponentType<P>) {
  return function WithTenantContext(props: P) {
    return (
      <TenantProvider>
        <Component {...props} />
      </TenantProvider>
    );
  };
}
