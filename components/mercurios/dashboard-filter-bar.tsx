'use client';

import { useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { useQuery } from '@tanstack/react-query';
import WarehouseFilter from '@/components/mercurios/warehouse-filter';
import { useWarehouse } from '@/components/mercurios/warehouse-context';
import prohandelClient from '@/lib/mercurios/clients/prohandel-client';
import { useTenant } from '@/lib/mercurios/tenant-context';

interface DashboardFilterBarProps {
  useRealData?: boolean;
}

export default function DashboardFilterBar({ useRealData = false }: DashboardFilterBarProps) {
  const { currentTenant } = useTenant();
  const {
    selectedWarehouseId,
    setSelectedWarehouseId,
    setSelectedWarehouseName,
    setWarehouses
  } = useWarehouse();

  // Fetch warehouses
  const { data: warehousesData } = useQuery({
    queryKey: ['warehouses', currentTenant.id, useRealData],
    queryFn: async () => {
      if (useRealData) {
        try {
          const response = await prohandelClient.getWarehouses();
          return response.data;
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

  // Update warehouse context when data changes
  useEffect(() => {
    if (warehousesData) {
      setWarehouses(warehousesData);
    }
  }, [warehousesData, setWarehouses]);

  // Update warehouse name when selection changes
  const handleWarehouseChange = (warehouseId: string | null) => {
    setSelectedWarehouseId(warehouseId);
    
    if (warehouseId && warehousesData) {
      const selectedWarehouse = warehousesData.find((w: any) => w.id === warehouseId);
      setSelectedWarehouseName(selectedWarehouse ? selectedWarehouse.name : null);
    } else {
      setSelectedWarehouseName(null);
    }
  };

  return (
    <Card className="p-2 flex flex-wrap items-center gap-2 mb-4">
      <div className="text-sm font-medium mr-2">Filter by:</div>
      <WarehouseFilter
        selectedWarehouseId={selectedWarehouseId}
        onChange={handleWarehouseChange}
        useRealData={useRealData}
      />
    </Card>
  );
}

// Mock warehouses for development
function getMockWarehouses() {
  return [
    { id: 'wh-001', name: 'Main Warehouse', code: 'MAIN', location: 'Berlin' },
    { id: 'wh-002', name: 'North Fulfillment Center', code: 'NFC', location: 'Hamburg' },
    { id: 'wh-003', name: 'South Distribution', code: 'SDIST', location: 'Munich' },
    { id: 'wh-004', name: 'East Logistics Hub', code: 'ELH', location: 'Dresden' },
    { id: 'wh-005', name: 'West Storage', code: 'WST', location: 'Cologne' },
  ];
}
