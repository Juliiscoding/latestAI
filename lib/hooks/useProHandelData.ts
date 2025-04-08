/**
 * React Hooks for ProHandel Data
 * 
 * These hooks provide a clean way for components to access ProHandel data 
 * with automatic loading states, error handling, and caching via React Query.
 */
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import * as prohandelData from '../data/prohandel';
import { 
  SalesSummary, 
  InventorySummary, 
  ProductSales, 
  InventoryRisk, 
  Warehouse,
  AIDataContext,
  TrendPoint
} from '../data/prohandel';

// Centralized query keys
export const QUERY_KEYS = {
  WAREHOUSES: 'warehouses',
  SALES: 'sales',
  TOP_PRODUCTS: 'topProducts',
  INVENTORY: 'inventory',
  STOCKOUT_RISKS: 'stockoutRisks',
  AI_CONTEXT: 'aiContext',
  SALES_COMPARISON: 'salesComparison',
  SALES_FORECAST: 'salesForecast'
};

/**
 * Get list of all warehouses/locations
 */
export const useWarehouses = (options?: UseQueryOptions<Warehouse[]>) => {
  return useQuery({
    queryKey: [QUERY_KEYS.WAREHOUSES],
    queryFn: () => prohandelData.getWarehouses(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
    ...options
  });
};

/**
 * Get sales data for a specific warehouse and time period
 */
export const useSalesData = (
  warehouseId?: string,
  period: '7d' | '30d' | '90d' = '30d',
  options?: UseQueryOptions<SalesSummary>
) => {
  return useQuery({
    queryKey: [QUERY_KEYS.SALES, warehouseId || 'all', period],
    queryFn: () => prohandelData.getSalesDataByWarehouse(warehouseId, period),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options
  });
};

/**
 * Get top products by revenue for a specific warehouse
 */
export const useTopProducts = (
  warehouseId?: string,
  limit: number = 10,
  options?: UseQueryOptions<ProductSales[]>
) => {
  return useQuery({
    queryKey: [QUERY_KEYS.TOP_PRODUCTS, warehouseId || 'all', limit],
    queryFn: () => prohandelData.getTopProductsByRevenue(warehouseId, limit),
    staleTime: 10 * 60 * 1000, // 10 minutes
    ...options
  });
};

/**
 * Get inventory data by category for a specific warehouse
 */
export const useInventoryData = (
  warehouseId?: string,
  options?: UseQueryOptions<InventorySummary>
) => {
  return useQuery({
    queryKey: [QUERY_KEYS.INVENTORY, warehouseId || 'all'],
    queryFn: () => prohandelData.getInventoryByCategory(warehouseId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options
  });
};

/**
 * Get stockout risk assessment for a specific warehouse
 */
export const useStockoutRisks = (
  warehouseId?: string,
  options?: UseQueryOptions<InventoryRisk[]>
) => {
  return useQuery({
    queryKey: [QUERY_KEYS.STOCKOUT_RISKS, warehouseId || 'all'],
    queryFn: () => prohandelData.getStockoutRiskAssessment(warehouseId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options
  });
};

/**
 * Get prepared AI assistant context data
 */
export const useAIAssistantContext = (
  warehouseId?: string,
  options?: UseQueryOptions<AIDataContext>
) => {
  return useQuery({
    queryKey: [QUERY_KEYS.AI_CONTEXT, warehouseId || 'all'],
    queryFn: () => prohandelData.getAIAssistantContext(warehouseId),
    staleTime: 10 * 60 * 1000, // 10 minutes
    ...options
  });
};

/**
 * Compare sales between two warehouses
 */
export const useSalesComparison = (
  warehouseId1: string,
  warehouseId2: string,
  period: '7d' | '30d' | '90d' = '30d',
  options?: UseQueryOptions<any>
) => {
  return useQuery({
    queryKey: [QUERY_KEYS.SALES_COMPARISON, warehouseId1, warehouseId2, period],
    queryFn: () => prohandelData.compareSalesBetweenWarehouses(warehouseId1, warehouseId2, period),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!warehouseId1 && !!warehouseId2 && (options?.enabled !== false),
    ...options
  });
};

/**
 * Get sales forecast for a specific warehouse
 */
export const useSalesForecast = (
  warehouseId?: string,
  days: number = 14,
  options?: UseQueryOptions<TrendPoint[]>
) => {
  return useQuery({
    queryKey: [QUERY_KEYS.SALES_FORECAST, warehouseId || 'all', days],
    queryFn: () => prohandelData.getSalesForecast(warehouseId, days),
    staleTime: 30 * 60 * 1000, // 30 minutes (forecasts don't change as frequently)
    ...options
  });
};
