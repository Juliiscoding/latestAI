/**
 * ProHandel Data Abstraction Layer
 * 
 * This layer provides business-logic focused functions that abstract away the 
 * direct API calls and transform the data into application-ready formats.
 */
import * as prohandelClient from '../mercurios/clients/prohandel-client';
import { DateTime } from 'luxon';

// Types for the abstracted data
export interface SalesSummary {
  totalRevenue: number;
  totalOrders: number;
  averageOrderValue: number;
  period: string;
  dateRange: {
    start: string;
    end: string;
  };
  byCategory?: CategorySales[];
  byProduct?: ProductSales[];
  trend?: TrendPoint[];
}

export interface CategorySales {
  categoryId: string;
  name: string;
  revenue: number;
  orderCount: number;
  percentOfTotal: number;
  growth: number; // Percentage growth compared to previous period
}

export interface ProductSales {
  productId: string;
  name: string;
  sku: string;
  categoryId: string;
  categoryName: string;
  revenue: number;
  unitsSold: number;
  averagePrice: number;
  inStock: boolean;
  stockLevel?: number;
  growth: number; // Percentage growth compared to previous period
}

export interface TrendPoint {
  date: string;
  revenue: number;
  orders: number;
}

export interface InventorySummary {
  totalProducts: number;
  totalValue: number;
  lowStockCount: number;
  outOfStockCount: number;
  byCategory: CategoryInventory[];
  riskProducts: InventoryRisk[];
}

export interface CategoryInventory {
  categoryId: string;
  name: string;
  productCount: number;
  inventoryValue: number;
  lowStockCount: number;
  outOfStockCount: number;
}

export interface InventoryRisk {
  productId: string;
  name: string;
  sku: string;
  categoryId: string;
  categoryName: string;
  stockLevel: number;
  reorderPoint: number;
  riskLevel: 'critical' | 'high' | 'medium' | 'low';
  lastRestockDate?: string;
  averageDailySales: number;
  daysUntilStockout?: number;
}

export interface Warehouse {
  id: string;
  name: string;
  description?: string;
  address?: string;
  active: boolean;
  isWebshop?: boolean;
}

export interface AIDataContext {
  salesTrends: {
    last7d: number;
    last30d: number;
    last90d: number;
    growthRate: number;
    segments: {
      categoryId: string;
      name: string;
      percentOfTotal: number;
      growth: number;
    }[];
  };
  inventoryHealth: {
    stockouts: number;
    atRisk: number;
    stable: number;
    riskItems: {
      productId: string;
      name: string;
      stockLevel: number;
      riskLevel: string;
      daysUntilStockout?: number;
    }[];
  };
  productInsights: {
    topProducts: {
      productId: string;
      name: string;
      revenue: number;
      growth: number;
    }[];
    underperformers: {
      productId: string;
      name: string;
      revenue: number;
      growth: number;
    }[];
  };
}

// Cache management
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds
const cache: Record<string, { timestamp: number; data: any }> = {};

function getCachedData<T>(key: string): T | null {
  const cachedItem = cache[key];
  if (cachedItem && Date.now() - cachedItem.timestamp < CACHE_DURATION) {
    return cachedItem.data as T;
  }
  return null;
}

function setCachedData<T>(key: string, data: T): void {
  cache[key] = {
    timestamp: Date.now(),
    data
  };
}

/**
 * Get list of all warehouses/locations
 */
export const getWarehouses = async (useRealData: boolean = true): Promise<Warehouse[]> => {
  const cacheKey = 'warehouses';
  const cached = getCachedData<Warehouse[]>(cacheKey);
  if (cached) return cached;

  const warehouses = await prohandelClient.getWarehouses(useRealData);
  setCachedData(cacheKey, warehouses);
  return warehouses;
};

/**
 * Get sales data by warehouse for a specific period
 * 
 * @param warehouseId Warehouse ID to filter by, undefined for all warehouses
 * @param period Time period to retrieve data for
 * @param useRealData Whether to use real or mock data
 */
export const getSalesDataByWarehouse = async (
  warehouseId?: string,
  period: '7d' | '30d' | '90d' = '30d',
  useRealData: boolean = true
): Promise<SalesSummary> => {
  const now = DateTime.now();
  let startDate: DateTime;
  
  // Calculate date range based on period
  switch (period) {
    case '7d':
      startDate = now.minus({ days: 7 });
      break;
    case '90d':
      startDate = now.minus({ days: 90 });
      break;
    case '30d':
    default:
      startDate = now.minus({ days: 30 });
      break;
  }

  const fromDate = startDate.toISODate();
  const toDate = now.toISODate();
  
  // Create a cache key based on parameters
  const cacheKey = `sales_${warehouseId || 'all'}_${period}`;
  const cached = getCachedData<SalesSummary>(cacheKey);
  if (cached) return cached;
  
  try {
    // Fetch raw sales data
    const salesData = await prohandelClient.getSales(fromDate, toDate, warehouseId, useRealData);
    
    if (!salesData || !Array.isArray(salesData) || salesData.length === 0) {
      return createEmptySalesSummary(period, fromDate, toDate);
    }
    
    // Process the raw data into the summary format
    const summary = processSalesData(salesData, period, fromDate, toDate);
    setCachedData(cacheKey, summary);
    
    return summary;
  } catch (error) {
    console.error(`Error fetching sales data for warehouse ${warehouseId}:`, error);
    return createEmptySalesSummary(period, fromDate, toDate);
  }
};

/**
 * Get top products by revenue with optional warehouse filter
 * 
 * @param warehouseId Optional warehouse ID to filter by
 * @param limit Number of top products to return
 * @param useRealData Whether to use real or mock data
 */
export const getTopProductsByRevenue = async (
  warehouseId?: string,
  limit: number = 10,
  useRealData: boolean = true
): Promise<ProductSales[]> => {
  // Try to get from cache first
  const cacheKey = `top_products_${warehouseId || 'all'}_${limit}`;
  const cached = getCachedData<ProductSales[]>(cacheKey);
  if (cached) return cached;
  
  try {
    // Get the last 30 days of sales data
    const salesSummary = await getSalesDataByWarehouse(warehouseId, '30d', useRealData);
    
    if (!salesSummary.byProduct || salesSummary.byProduct.length === 0) {
      return [];
    }
    
    // Sort products by revenue and take the top ones
    const topProducts = [...salesSummary.byProduct]
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, limit);
    
    setCachedData(cacheKey, topProducts);
    return topProducts;
  } catch (error) {
    console.error('Error fetching top products by revenue:', error);
    return [];
  }
};

/**
 * Get inventory data by category with optional warehouse filter
 * 
 * @param warehouseId Optional warehouse ID to filter by
 * @param useRealData Whether to use real or mock data
 */
export const getInventoryByCategory = async (
  warehouseId?: string,
  useRealData: boolean = true
): Promise<InventorySummary> => {
  const cacheKey = `inventory_${warehouseId || 'all'}`;
  const cached = getCachedData<InventorySummary>(cacheKey);
  if (cached) return cached;
  
  try {
    // Get inventory data
    const inventoryData = await fetchInventoryData(warehouseId, useRealData);
    
    // Process raw inventory data
    const summary = processInventoryData(inventoryData, warehouseId);
    setCachedData(cacheKey, summary);
    
    return summary;
  } catch (error) {
    console.error(`Error fetching inventory data for warehouse ${warehouseId}:`, error);
    return createEmptyInventorySummary();
  }
};

/**
 * Get stockout risks with enhanced risk assessment
 * 
 * @param warehouseId Optional warehouse ID to filter by
 * @param useRealData Whether to use real or mock data
 */
export const getStockoutRiskAssessment = async (
  warehouseId?: string,
  useRealData: boolean = true
): Promise<InventoryRisk[]> => {
  const cacheKey = `stockout_risks_${warehouseId || 'all'}`;
  const cached = getCachedData<InventoryRisk[]>(cacheKey);
  if (cached) return cached;
  
  try {
    // Get basic stockout risks from client
    const stockoutRisks = await prohandelClient.getStockoutRisks(warehouseId, useRealData);
    
    // Fetch sales data to calculate average daily sales for better risk assessment
    const last30DaysSales = await getSalesDataByWarehouse(warehouseId, '30d', useRealData);
    
    // Enrich stockout risks with sales data for better risk assessment
    const enrichedRisks = enrichStockoutRisks(stockoutRisks, last30DaysSales);
    setCachedData(cacheKey, enrichedRisks);
    
    return enrichedRisks;
  } catch (error) {
    console.error(`Error fetching stockout risk assessment for warehouse ${warehouseId}:`, error);
    return [];
  }
};

/**
 * Get data prepared for AI Assistant context
 * 
 * @param warehouseId Optional warehouse ID to filter by
 * @param useRealData Whether to use real or mock data
 */
export const getAIAssistantContext = async (
  warehouseId?: string,
  useRealData: boolean = true
): Promise<AIDataContext> => {
  try {
    // Fetch all the relevant data needed for the AI context
    const [sales7d, sales30d, sales90d, inventory, topProducts] = await Promise.all([
      getSalesDataByWarehouse(warehouseId, '7d', useRealData),
      getSalesDataByWarehouse(warehouseId, '30d', useRealData),
      getSalesDataByWarehouse(warehouseId, '90d', useRealData),
      getInventoryByCategory(warehouseId, useRealData),
      getTopProductsByRevenue(warehouseId, 5, useRealData)
    ]);
    
    // Calculate growth rate (comparing 30d to previous 30d)
    const growthRate = calculateGrowthRate(sales30d, sales90d);
    
    // Format the data for the AI context
    const aiContext: AIDataContext = {
      salesTrends: {
        last7d: sales7d.totalRevenue,
        last30d: sales30d.totalRevenue,
        last90d: sales90d.totalRevenue,
        growthRate,
        segments: sales30d.byCategory?.map(category => ({
          categoryId: category.categoryId,
          name: category.name,
          percentOfTotal: category.percentOfTotal,
          growth: category.growth
        })) || []
      },
      inventoryHealth: {
        stockouts: inventory.outOfStockCount,
        atRisk: inventory.lowStockCount,
        stable: inventory.totalProducts - inventory.lowStockCount - inventory.outOfStockCount,
        riskItems: inventory.riskProducts.map(product => ({
          productId: product.productId,
          name: product.name,
          stockLevel: product.stockLevel,
          riskLevel: product.riskLevel,
          daysUntilStockout: product.daysUntilStockout
        }))
      },
      productInsights: {
        topProducts: topProducts.slice(0, 5).map(product => ({
          productId: product.productId,
          name: product.name,
          revenue: product.revenue,
          growth: product.growth
        })),
        underperformers: sales30d.byProduct
          ?.filter(product => product.growth < 0)
          .sort((a, b) => a.growth - b.growth)
          .slice(0, 5)
          .map(product => ({
            productId: product.productId,
            name: product.name,
            revenue: product.revenue,
            growth: product.growth
          })) || []
      }
    };
    
    return aiContext;
  } catch (error) {
    console.error('Error creating AI assistant context:', error);
    return createEmptyAIContext();
  }
};

/**
 * Get sales comparison between two warehouses
 * 
 * @param warehouseId1 First warehouse ID
 * @param warehouseId2 Second warehouse ID
 * @param period Time period for comparison
 * @param useRealData Whether to use real or mock data
 */
export const compareSalesBetweenWarehouses = async (
  warehouseId1: string,
  warehouseId2: string,
  period: '7d' | '30d' | '90d' = '30d',
  useRealData: boolean = true
): Promise<{
  warehouse1: SalesSummary;
  warehouse2: SalesSummary;
  revenueDiff: number;
  revenueDiffPercent: number;
  ordersDiff: number;
  ordersDiffPercent: number;
  topPerformingCategories: {
    categoryId: string;
    name: string;
    warehouse1Revenue: number;
    warehouse2Revenue: number;
    diffPercent: number;
  }[];
}> => {
  try {
    // Get sales data for both warehouses
    const [warehouse1Sales, warehouse2Sales] = await Promise.all([
      getSalesDataByWarehouse(warehouseId1, period, useRealData),
      getSalesDataByWarehouse(warehouseId2, period, useRealData)
    ]);
    
    // Calculate differences
    const revenueDiff = warehouse1Sales.totalRevenue - warehouse2Sales.totalRevenue;
    const revenueDiffPercent = (revenueDiff / warehouse2Sales.totalRevenue) * 100;
    const ordersDiff = warehouse1Sales.totalOrders - warehouse2Sales.totalOrders;
    const ordersDiffPercent = (ordersDiff / warehouse2Sales.totalOrders) * 100;
    
    // Compare categories
    const topPerformingCategories = compareCategories(
      warehouse1Sales.byCategory || [],
      warehouse2Sales.byCategory || []
    );
    
    return {
      warehouse1: warehouse1Sales,
      warehouse2: warehouse2Sales,
      revenueDiff,
      revenueDiffPercent,
      ordersDiff,
      ordersDiffPercent,
      topPerformingCategories
    };
  } catch (error) {
    console.error('Error comparing sales between warehouses:', error);
    throw new Error('Failed to compare warehouse sales');
  }
};

/**
 * Get forecast data for a specific warehouse
 * 
 * @param warehouseId Warehouse ID to forecast for
 * @param days Number of days to forecast
 * @param useRealData Whether to use real or mock data
 */
export const getSalesForecast = async (
  warehouseId?: string, 
  days: number = 14,
  useRealData: boolean = true
): Promise<TrendPoint[]> => {
  try {
    // Get historical sales data for forecasting
    const historicalSales = await getSalesDataByWarehouse(warehouseId, '90d', useRealData);
    
    if (!historicalSales.trend || historicalSales.trend.length === 0) {
      return createEmptyForecast(days);
    }
    
    // Calculate forecast based on historical trend
    // This is a simple linear forecast, could be replaced with more sophisticated algorithms
    const forecast = generateSimpleForecast(historicalSales.trend, days);
    return forecast;
  } catch (error) {
    console.error(`Error generating sales forecast for warehouse ${warehouseId}:`, error);
    return createEmptyForecast(days);
  }
};

// Helper functions for data processing
// These would be implemented below with actual business logic

function processSalesData(salesData: any[], period: string, fromDate: string, toDate: string): SalesSummary {
  // Implementation would go here
  // This would aggregate the raw sales data into the SalesSummary format
  // For this example, we'll return a placeholder
  return createEmptySalesSummary(period, fromDate, toDate);
}

function createEmptySalesSummary(period: string, fromDate: string, toDate: string): SalesSummary {
  return {
    totalRevenue: 0,
    totalOrders: 0,
    averageOrderValue: 0,
    period,
    dateRange: {
      start: fromDate,
      end: toDate
    },
    byCategory: [],
    byProduct: [],
    trend: []
  };
}

async function fetchInventoryData(warehouseId?: string, useRealData: boolean = true): Promise<any[]> {
  // In a real implementation, this would fetch inventory data from the ProHandel API
  // For now, we'll return mock data
  return [];
}

function processInventoryData(inventoryData: any[], warehouseId?: string): InventorySummary {
  // Implementation would process raw inventory data
  // For now, we'll return a placeholder
  return createEmptyInventorySummary();
}

function createEmptyInventorySummary(): InventorySummary {
  return {
    totalProducts: 0,
    totalValue: 0,
    lowStockCount: 0,
    outOfStockCount: 0,
    byCategory: [],
    riskProducts: []
  };
}

function enrichStockoutRisks(stockoutRisks: any[], salesData: SalesSummary): InventoryRisk[] {
  // This would enrich stockout risks with sales velocity data
  // For now, we'll return an empty array
  return [];
}

function calculateGrowthRate(currentPeriod: SalesSummary, previousPeriod: SalesSummary): number {
  if (!previousPeriod.totalRevenue) return 0;
  return ((currentPeriod.totalRevenue - previousPeriod.totalRevenue) / previousPeriod.totalRevenue) * 100;
}

function compareCategories(
  categories1: CategorySales[],
  categories2: CategorySales[]
): { categoryId: string; name: string; warehouse1Revenue: number; warehouse2Revenue: number; diffPercent: number }[] {
  // This would compare category performance between warehouses
  return [];
}

function createEmptyAIContext(): AIDataContext {
  return {
    salesTrends: {
      last7d: 0,
      last30d: 0,
      last90d: 0,
      growthRate: 0,
      segments: []
    },
    inventoryHealth: {
      stockouts: 0,
      atRisk: 0,
      stable: 0,
      riskItems: []
    },
    productInsights: {
      topProducts: [],
      underperformers: []
    }
  };
}

function generateSimpleForecast(historicalTrend: TrendPoint[], days: number): TrendPoint[] {
  // This would generate a simple forecast based on historical trend
  // For now, we'll return an empty array
  return createEmptyForecast(days);
}

function createEmptyForecast(days: number): TrendPoint[] {
  const forecast: TrendPoint[] = [];
  const today = DateTime.now();
  
  for (let i = 1; i <= days; i++) {
    const forecastDate = today.plus({ days: i });
    forecast.push({
      date: forecastDate.toISODate(),
      revenue: 0,
      orders: 0
    });
  }
  
  return forecast;
}
