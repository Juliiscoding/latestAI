'use client';

import { createContext, useState, useContext, ReactNode } from 'react';
import { Warehouse } from '@/components/mercurios/warehouse-filter';

interface WarehouseContextType {
  selectedWarehouseId: string | null;
  setSelectedWarehouseId: (id: string | null) => void;
  selectedWarehouseName: string | null;
  setSelectedWarehouseName: (name: string | null) => void;
  warehouses: Warehouse[];
  setWarehouses: (warehouses: Warehouse[]) => void;
}

const WarehouseContext = createContext<WarehouseContextType>({
  selectedWarehouseId: null,
  setSelectedWarehouseId: () => {},
  selectedWarehouseName: null,
  setSelectedWarehouseName: () => {},
  warehouses: [],
  setWarehouses: () => {},
});

export function WarehouseProvider({ children }: { children: ReactNode }) {
  const [selectedWarehouseId, setSelectedWarehouseId] = useState<string | null>(null);
  const [selectedWarehouseName, setSelectedWarehouseName] = useState<string | null>(null);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);

  return (
    <WarehouseContext.Provider
      value={{
        selectedWarehouseId,
        setSelectedWarehouseId,
        selectedWarehouseName,
        setSelectedWarehouseName,
        warehouses,
        setWarehouses,
      }}
    >
      {children}
    </WarehouseContext.Provider>
  );
}

export function useWarehouse() {
  const context = useContext(WarehouseContext);
  if (!context) {
    throw new Error('useWarehouse must be used within a WarehouseProvider');
  }
  return context;
}
