'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';

// Define tenant interface
export interface Tenant {
  id: string;
  name: string;
  logo?: string;
  primaryColor?: string;
  secondaryColor?: string;
  apiEndpoint?: string;
}

// Default tenant
const DEFAULT_TENANT: Tenant = {
  id: 'prohandel-demo',
  name: 'ProHandel Demo',
  primaryColor: '#3b82f6',
  secondaryColor: '#10b981',
};

// Context interface
interface TenantContextType {
  currentTenant: Tenant;
  setTenant: (tenant: Tenant) => void;
  availableTenants: Tenant[];
  isLoading: boolean;
}

// Create the context
const TenantContext = createContext<TenantContextType>({
  currentTenant: DEFAULT_TENANT,
  setTenant: () => {},
  availableTenants: [DEFAULT_TENANT],
  isLoading: true,
});

// Sample tenants for demo purposes
const SAMPLE_TENANTS: Tenant[] = [
  DEFAULT_TENANT,
  {
    id: 'fashion-retail',
    name: 'Fashion Retail',
    primaryColor: '#ec4899',
    secondaryColor: '#8b5cf6',
  },
  {
    id: 'electronics-store',
    name: 'Electronics Store',
    primaryColor: '#f97316',
    secondaryColor: '#06b6d4',
  },
  {
    id: 'grocery-chain',
    name: 'Grocery Chain',
    primaryColor: '#22c55e',
    secondaryColor: '#eab308',
  },
];

// Provider component
export function TenantProvider({ children }: { children: ReactNode }) {
  const [currentTenant, setCurrentTenant] = useState<Tenant>(DEFAULT_TENANT);
  const [availableTenants, setAvailableTenants] = useState<Tenant[]>([DEFAULT_TENANT]);
  const [isLoading, setIsLoading] = useState(true);

  // Load tenants on mount
  useEffect(() => {
    const loadTenants = async () => {
      try {
        // In a real app, you would fetch tenants from an API
        // For demo purposes, we'll use the sample tenants
        setAvailableTenants(SAMPLE_TENANTS);
        
        // Get tenant from cookie or use default
        const savedTenantId = Cookies.get('mcp_tenant_id');
        if (savedTenantId) {
          const savedTenant = SAMPLE_TENANTS.find(t => t.id === savedTenantId);
          if (savedTenant) {
            setCurrentTenant(savedTenant);
          }
        }
      } catch (error) {
        console.error('Error loading tenants:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadTenants();
  }, []);

  // Set tenant and save to cookie
  const setTenant = (tenant: Tenant) => {
    setCurrentTenant(tenant);
    Cookies.set('mcp_tenant_id', tenant.id, { expires: 30 });
    
    // Apply tenant theme
    if (tenant.primaryColor) {
      document.documentElement.style.setProperty('--primary', tenant.primaryColor);
    }
    if (tenant.secondaryColor) {
      document.documentElement.style.setProperty('--secondary', tenant.secondaryColor);
    }
  };

  return (
    <TenantContext.Provider
      value={{
        currentTenant,
        setTenant,
        availableTenants,
        isLoading,
      }}
    >
      {children}
    </TenantContext.Provider>
  );
}

// Custom hook to use the tenant context
export function useTenant() {
  const context = useContext(TenantContext);
  if (context === undefined) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  return context;
}

// Utility function to get the current tenant ID
export function getCurrentTenantId(): string {
  if (typeof window !== 'undefined') {
    return Cookies.get('mcp_tenant_id') || 'prohandel-demo';
  }
  return 'prohandel-demo';
}
