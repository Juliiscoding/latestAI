import { useQuery } from '@tanstack/react-query';
import prohandelClient from '@/lib/mercurios/clients/prohandel-client';

/**
 * Custom hook for fetching ProHandel data with React Query
 * Provides consistent caching, loading states, and error handling
 */
export function useProHandelData<T>(
  queryKey: string,
  dataFetcher: () => Promise<T>,
  mockDataFetcher: () => Promise<T> | T,
  options: {
    useRealData?: boolean;
    enabled?: boolean;
    staleTime?: number;
    refetchOnWindowFocus?: boolean;
    warehouseId?: string | null;
  } = {}
) {
  const {
    useRealData = false,
    enabled = true,
    staleTime = 5 * 60 * 1000, // 5 minutes by default
    refetchOnWindowFocus = false,
    warehouseId = null,
  } = options;

  return useQuery({
    queryKey: [queryKey, { useRealData, warehouseId }],
    queryFn: async () => {
      if (useRealData) {
        console.log(`Fetching real ProHandel data for ${queryKey}...`);
        try {
          return await dataFetcher();
        } catch (err) {
          console.error(`Error fetching ${queryKey} from ProHandel:`, err);
          // Fallback to mock data in case of error
          console.log(`Falling back to mock data for ${queryKey}`);
          return mockDataFetcher();
        }
      } else {
        console.log(`Using mock data for ${queryKey}...`);
        return mockDataFetcher();
      }
    },
    enabled,
    staleTime,
    refetchOnWindowFocus,
  });
}

/**
 * Hook for fetching stockout risk data
 */
export function useStockoutRisk(options: { 
  useRealData?: boolean; 
  enabled?: boolean;
  warehouseId?: string | null;
} = {}) {
  const { warehouseId = null } = options;
  
  return useProHandelData(
    'stockoutRisk',
    () => {
      // If warehouse ID is provided, pass it to the API call
      if (warehouseId) {
        return prohandelClient.getStockoutDataWithWarehouse(warehouseId);
      }
      return prohandelClient.getStockoutDataSimple();
    },
    () => prohandelClient.calculateStockoutRisk(),
    options
  );
}

/**
 * Hook for fetching sales trend data
 */
export function useSalesTrend(
  period: '7days' | '30days' | '90days' | 'year' = '30days',
  options: { useRealData?: boolean; enabled?: boolean } = {}
) {
  return useProHandelData(
    `salesTrend-${period}`,
    async () => {
      // Calculate date range based on selected period
      const today = new Date();
      const fromDate = new Date(today);
      
      switch (period) {
        case '7days':
          fromDate.setDate(today.getDate() - 7);
          break;
        case '30days':
          fromDate.setDate(today.getDate() - 30);
          break;
        case '90days':
          fromDate.setDate(today.getDate() - 90);
          break;
        case 'year':
          fromDate.setFullYear(today.getFullYear() - 1);
          break;
      }
      
      const from = fromDate.toISOString().split('T')[0];
      const to = today.toISOString().split('T')[0];
      
      // Get sales data from ProHandel
      const salesData = await prohandelClient.getSales({
        from,
        to,
        groupBy: period === '7days' ? 'day' : period === 'year' ? 'month' : 'week'
      });
      
      // Transform the data for the chart
      return salesData.data.map((item: any) => ({
        date: item.date,
        sales: item.total_amount,
        orders: item.order_count,
      }));
    },
    () => {
      // Generate mock data
      const data = [];
      const today = new Date();
      let numPoints = 0;
      let dateFormat = '';
      
      switch (period) {
        case '7days':
          numPoints = 7;
          dateFormat = 'day';
          break;
        case '30days':
          numPoints = 4; // 4 weeks
          dateFormat = 'week';
          break;
        case '90days':
          numPoints = 12; // 12 weeks
          dateFormat = 'week';
          break;
        case 'year':
          numPoints = 12; // 12 months
          dateFormat = 'month';
          break;
      }
      
      for (let i = 0; i < numPoints; i++) {
        const date = new Date(today);
        
        if (dateFormat === 'day') {
          date.setDate(date.getDate() - (numPoints - i - 1));
        } else if (dateFormat === 'week') {
          date.setDate(date.getDate() - (numPoints - i - 1) * 7);
        } else if (dateFormat === 'month') {
          date.setMonth(date.getMonth() - (numPoints - i - 1));
        }
        
        const formattedDate = dateFormat === 'day' 
          ? date.toLocaleDateString('en-US', { weekday: 'short' })
          : dateFormat === 'week'
            ? `W${i + 1}`
            : date.toLocaleDateString('en-US', { month: 'short' });
        
        data.push({
          date: formattedDate,
          sales: Math.floor(Math.random() * 5000) + 3000,
          orders: Math.floor(Math.random() * 50) + 20,
        });
      }
      
      return data;
    },
    options
  );
}

/**
 * Hook for fetching inventory analytics data
 */
export function useInventoryAnalytics(options: { useRealData?: boolean; enabled?: boolean } = {}) {
  return useProHandelData(
    'inventoryAnalytics',
    async () => {
      const today = new Date();
      const thirtyDaysAgo = new Date(today);
      thirtyDaysAgo.setDate(today.getDate() - 30);
      
      const from = thirtyDaysAgo.toISOString().split('T')[0];
      const to = today.toISOString().split('T')[0];
      
      return prohandelClient.getInventoryAnalytics({ from, to });
    },
    () => ({
      data: {
        totalValue: 143245.50,
        changePercentage: 2.5,
        productCount: 1283,
        newItems: 12,
        quarterlyTrends: [45, 15, 25, 15],
        stockHealth: 86,
        stockHealthTarget: 89,
        stockDistribution: {
          low: 15,
          optimal: 65,
          excess: 20,
        }
      }
    }),
    options
  );
}
