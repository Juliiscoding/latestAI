"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { Tenant } from '@prisma/client';

interface TenantContextType {
  currentTenant: Tenant | null;
  setCurrentTenant: (tenant: Tenant | null) => void;
  isLoading: boolean;
}

const TenantContext = createContext<TenantContextType>({
  currentTenant: null,
  setCurrentTenant: () => {},
  isLoading: true
});

export const useTenant = () => useContext(TenantContext);

export function TenantProvider({ children }: { children: React.ReactNode }) {
  const [currentTenant, setCurrentTenant] = useState<Tenant | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadTenant() {
      try {
        // Wir laden den aktuellen Tenant basierend auf der URL oder einem Cookie
        const response = await fetch('/api/tenant/current');
        if (response.ok) {
          const data = await response.json();
          setCurrentTenant(data.tenant);
        }
      } catch (error) {
        console.error("Failed to load tenant:", error);
      } finally {
        setIsLoading(false);
      }
    }

    loadTenant();
  }, []);

  return (
    <TenantContext.Provider value={{ currentTenant, setCurrentTenant, isLoading }}>
      {children}
    </TenantContext.Provider>
  );
}

// Hinweis: Die Funktion extractTenantFromHostname wurde in lib/tenant/utils.ts verschoben
// damit sie sowohl auf dem Server als auch auf dem Client verwendet werden kann
