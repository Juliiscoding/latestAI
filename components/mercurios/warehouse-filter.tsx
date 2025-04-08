'use client';

import { useState, useEffect } from 'react';
import { Check, ChevronsUpDown, Warehouse } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { useQuery } from '@tanstack/react-query';
import { cn } from '@/lib/utils';
import prohandelClient from '@/lib/mercurios/clients/prohandel-client';
import { useTenant } from '@/lib/mercurios/tenant-context';

export interface Warehouse {
  id: string;
  name: string;
  code?: string;
  location?: string;
}

interface WarehouseFilterProps {
  onChange: (warehouseId: string | null) => void;
  selectedWarehouseId: string | null;
  size?: 'default' | 'sm';
  showAllOption?: boolean;
  className?: string;
  useRealData?: boolean;
}

export default function WarehouseFilter({
  onChange,
  selectedWarehouseId,
  size = 'default',
  showAllOption = true,
  className,
  useRealData = false,
}: WarehouseFilterProps) {
  const [open, setOpen] = useState(false);
  const { currentTenant } = useTenant();
  
  // Fetch warehouses from the API
  const { data: warehousesData, isLoading } = useQuery({
    queryKey: ['warehouses', currentTenant.id, useRealData],
    queryFn: async () => {
      if (useRealData) {
        try {
          // Call the ProHandel API to get warehouses
          const response = await prohandelClient.getWarehouses();
          return response.data.map((warehouse: Warehouse) => ({
            id: warehouse.id,
            name: warehouse.name,
            code: warehouse.code,
            location: warehouse.location,
          }));
        } catch (error) {
          console.error('Error fetching warehouses:', error);
          return getMockWarehouses();
        }
      } else {
        return getMockWarehouses();
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const warehouses = warehousesData || [];
  
  // Set the first warehouse as default if none is selected and warehouses are loaded
  useEffect(() => {
    if (warehouses.length > 0 && selectedWarehouseId === null && !showAllOption) {
      onChange(warehouses[0].id);
    }
  }, [warehouses, selectedWarehouseId, onChange, showAllOption]);

  // Find the selected warehouse
  const selectedWarehouse = selectedWarehouseId
    ? warehouses.find((warehouse) => warehouse.id === selectedWarehouseId)
    : null;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            "justify-between",
            size === 'sm' ? 'h-8 text-xs' : '',
            className
          )}
          disabled={isLoading}
        >
          <div className="flex items-center">
            <Warehouse className="mr-2 h-4 w-4" />
            {selectedWarehouseId 
              ? selectedWarehouse?.name || 'Loading...'
              : 'All Warehouses'}
          </div>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="p-0" align="start" sideOffset={5}>
        <Command>
          <CommandInput placeholder="Search warehouse..." />
          <CommandList>
            <CommandEmpty>No warehouse found.</CommandEmpty>
            <CommandGroup>
              {showAllOption && (
                <CommandItem
                  onSelect={() => {
                    onChange(null);
                    setOpen(false);
                  }}
                  className="flex items-center"
                >
                  <div className="flex items-center">
                    <Warehouse className="mr-2 h-4 w-4" />
                    <span>All Warehouses</span>
                  </div>
                  {selectedWarehouseId === null && (
                    <Check className="ml-auto h-4 w-4" />
                  )}
                </CommandItem>
              )}
              {warehouses.map((warehouse: Warehouse) => (
                <CommandItem
                  key={warehouse.id}
                  onSelect={() => {
                    onChange(warehouse.id);
                    setOpen(false);
                  }}
                  className="flex items-center"
                >
                  <div className="flex items-center">
                    <Warehouse className="mr-2 h-4 w-4" />
                    <span>{warehouse.name}</span>
                    {warehouse.code && (
                      <span className="ml-2 text-xs text-muted-foreground">
                        ({warehouse.code})
                      </span>
                    )}
                  </div>
                  {selectedWarehouseId === warehouse.id && (
                    <Check className="ml-auto h-4 w-4" />
                  )}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

// Mock data for development
function getMockWarehouses(): Warehouse[] {
  return [
    { id: 'wh-001', name: 'Main Warehouse', code: 'MAIN', location: 'Berlin' },
    { id: 'wh-002', name: 'North Fulfillment Center', code: 'NFC', location: 'Hamburg' },
    { id: 'wh-003', name: 'South Distribution', code: 'SDIST', location: 'Munich' },
    { id: 'wh-004', name: 'East Logistics Hub', code: 'ELH', location: 'Dresden' },
    { id: 'wh-005', name: 'West Storage', code: 'WST', location: 'Cologne' },
  ];
}
