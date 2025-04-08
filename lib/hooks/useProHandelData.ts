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

// Force real data by default (no mock data)
const USE_REAL_DATA = true;

/**
 * Get list of all warehouses/locations
 */
export const useWarehouses = (options?: Partial<UseQueryOptions<Warehouse[]>>) => {
  return useQuery<Warehouse[]>({
    queryKey: [QUERY_KEYS.WAREHOUSES],
    queryFn: () => prohandelData.getWarehouses(USE_REAL_DATA),
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
  options?: Partial<UseQueryOptions<SalesSummary>>
) => {
  return useQuery<SalesSummary>({
    queryKey: [QUERY_KEYS.SALES, warehouseId || 'all', period],
    queryFn: () => prohandelData.getSalesDataByWarehouse(warehouseId, period, USE_REAL_DATA),
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
  options?: Partial<UseQueryOptions<ProductSales[]>>
) => {
  return useQuery<ProductSales[]>({
    queryKey: [QUERY_KEYS.TOP_PRODUCTS, warehouseId || 'all', limit],
    queryFn: () => prohandelData.getTopProductsByRevenue(warehouseId, limit, USE_REAL_DATA),
    staleTime: 10 * 60 * 1000, // 10 minutes
    ...options
  });
};

/**
 * Get inventory data by category for a specific warehouse
 */
export const useInventoryData = (
  warehouseId?: string,
  options?: Partial<UseQueryOptions<InventorySummary>>
) => {
  return useQuery<InventorySummary>({
    queryKey: [QUERY_KEYS.INVENTORY, warehouseId || 'all'],
    queryFn: () => prohandelData.getInventoryByCategory(warehouseId, USE_REAL_DATA),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options
  });
};

/**
 * Get stockout risk assessment for a specific warehouse
 */
export const useStockoutRisks = (
  warehouseId?: string,
  options?: Partial<UseQueryOptions<InventoryRisk[]>>
) => {
  return useQuery<InventoryRisk[]>({
    queryKey: [QUERY_KEYS.STOCKOUT_RISKS, warehouseId || 'all'],
    queryFn: () => prohandelData.getStockoutRiskAssessment(warehouseId, USE_REAL_DATA),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options
  });
};

/**
 * Get prepared AI assistant context data
 */
export const useAIAssistantContext = (
  warehouseId?: string,
  options?: Partial<UseQueryOptions<AIDataContext>>
) => {
  return useQuery<AIDataContext>({
    queryKey: [QUERY_KEYS.AI_CONTEXT, warehouseId || 'all'],
    queryFn: () => prohandelData.getAIAssistantContext(warehouseId, USE_REAL_DATA),
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
  options?: Partial<UseQueryOptions<any>>
) => {
  return useQuery<any>({
    queryKey: [QUERY_KEYS.SALES_COMPARISON, warehouseId1, warehouseId2, period],
    queryFn: () => prohandelData.compareSalesBetweenWarehouses(warehouseId1, warehouseId2, period, USE_REAL_DATA),
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
  options?: Partial<UseQueryOptions<TrendPoint[]>>
) => {
  return useQuery<TrendPoint[]>({
    queryKey: [QUERY_KEYS.SALES_FORECAST, warehouseId || 'all', days],
    queryFn: () => prohandelData.getSalesForecast(warehouseId, days, USE_REAL_DATA),
    staleTime: 30 * 60 * 1000, // 30 minutes (forecasts don't change as frequently)
    ...options
  });
};
