'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useTenant, Tenant } from '@/lib/mercurios/tenant-context';
import { Building2, Check, ChevronDown } from 'lucide-react';

export default function TenantSelector() {
  const { currentTenant, setTenant, availableTenants } = useTenant();
  const [open, setOpen] = useState(false);

  const handleSelect = (tenant: Tenant) => {
    setTenant(tenant);
    setOpen(false);
    // Reload the page to refresh data with new tenant
    window.location.reload();
  };

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          <Building2 className="h-4 w-4" />
          <span className="hidden md:inline">{currentTenant.name}</span>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>Switch Environment</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {availableTenants.map((tenant) => (
          <DropdownMenuItem
            key={tenant.id}
            className="flex items-center justify-between cursor-pointer"
            onClick={() => handleSelect(tenant)}
          >
            <span>{tenant.name}</span>
            {tenant.id === currentTenant.id && <Check className="h-4 w-4" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
