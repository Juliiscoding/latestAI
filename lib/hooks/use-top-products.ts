import { useQuery } from '@tanstack/react-query';
import prohandelClient from '@/lib/mercurios/clients/prohandel-client';
import { useTenant } from '@/lib/mercurios/tenant-context';

export interface TopProduct {
  id: string;
  name: string;
  quantity: number;
  revenue: number;
  category: string;
  percentageOfTotal: number;
}

export interface TopProductsData {
  products: TopProduct[];
  totalRevenue: number;
  totalQuantity: number;
  startDate: string;
  endDate: string;
}

/**
 * Hook for fetching top products by sales quantity or revenue
 */
export function useTopProducts(
  period: '7days' | '30days' | '90days' | 'year' = '30days',
  sortBy: 'quantity' | 'revenue' = 'quantity',
  limit: number = 10,
  options: { 
    useRealData?: boolean; 
    enabled?: boolean;
    warehouseId?: string | null;
  } = {}
) {
  const { currentTenant } = useTenant();
  const { 
    useRealData = false, 
    enabled = true,
    warehouseId = null
  } = options;

  return useQuery({
    queryKey: ['topProducts', period, sortBy, limit, useRealData, currentTenant.id, warehouseId],
    queryFn: async () => {
      if (useRealData) {
        try {
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
          
          // Fetch sales data including product information
          const salesData = await prohandelClient.getSales({
            from,
            to,
            // Add location_id if warehouse is selected
            ...(warehouseId ? { location_id: warehouseId } : {}),
            // TypeScript doesn't know about this property, but it's supported by the API
            // @ts-ignore
            include_articles: true,
          });
          
          // Process the sales data to get top products
          const productMap = new Map<string, {
            id: string;
            name: string;
            quantity: number;
            revenue: number;
            category: string;
          }>();
          
          // Aggregate sales by product
          salesData.data.forEach((sale: any) => {
            sale.items.forEach((item: any) => {
              const productId = item.article_id;
              const existingProduct = productMap.get(productId);
              
              if (existingProduct) {
                existingProduct.quantity += item.quantity;
                existingProduct.revenue += item.price * item.quantity;
              } else {
                productMap.set(productId, {
                  id: productId,
                  name: item.article_name || `Product ${productId}`,
                  quantity: item.quantity,
                  revenue: item.price * item.quantity,
                  category: item.category_name || 'Uncategorized',
                });
              }
            });
          });
          
          // Convert map to array and sort
          let products = Array.from(productMap.values());
          
          // Sort by the selected metric
          products = products.sort((a, b) => 
            sortBy === 'quantity' 
              ? b.quantity - a.quantity 
              : b.revenue - a.revenue
          );
          
          // Calculate totals
          const totalRevenue = products.reduce((sum, product) => sum + product.revenue, 0);
          const totalQuantity = products.reduce((sum, product) => sum + product.quantity, 0);
          
          // Add percentage of total and limit the results
          const topProducts = products.slice(0, limit).map(product => ({
            ...product,
            percentageOfTotal: sortBy === 'quantity'
              ? (product.quantity / totalQuantity) * 100
              : (product.revenue / totalRevenue) * 100
          }));
          
          return {
            products: topProducts,
            totalRevenue,
            totalQuantity,
            startDate: from,
            endDate: to,
          };
        } catch (error) {
          console.error('Error fetching top products:', error);
          // Fallback to mock data
          return getMockTopProducts(period, sortBy, limit);
        }
      } else {
        // Use mock data
        return getMockTopProducts(period, sortBy, limit);
      }
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Generate mock top products data for development and testing
 */
function getMockTopProducts(
  period: '7days' | '30days' | '90days' | 'year',
  sortBy: 'quantity' | 'revenue',
  limit: number
): TopProductsData {
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
  
  // Sample product names and categories
  const productOptions = [
    { name: 'Premium T-Shirt', category: 'Clothing' },
    { name: 'Designer Jeans', category: 'Clothing' },
    { name: 'Wireless Headphones', category: 'Electronics' },
    { name: 'Smart Watch', category: 'Electronics' },
    { name: 'Running Shoes', category: 'Footwear' },
    { name: 'Protein Powder', category: 'Nutrition' },
    { name: 'Yoga Mat', category: 'Fitness' },
    { name: 'Coffee Maker', category: 'Home' },
    { name: 'Desk Lamp', category: 'Home' },
    { name: 'Backpack', category: 'Accessories' },
    { name: 'Sunglasses', category: 'Accessories' },
    { name: 'Water Bottle', category: 'Sports' },
    { name: 'Notebook', category: 'Stationery' },
    { name: 'Bluetooth Speaker', category: 'Electronics' },
    { name: 'Face Cream', category: 'Beauty' },
  ];
  
  // Generate random products with sales data
  const products: TopProduct[] = productOptions.slice(0, limit).map((product, index) => {
    // Create realistic sales numbers based on product index (higher index = lower sales)
    const baseQuantity = Math.round(1000 / (index + 1));
    const variability = baseQuantity * 0.2; // 20% variability
    
    const quantity = Math.round(baseQuantity + (Math.random() * variability * 2 - variability));
    const unitPrice = 20 + Math.round(Math.random() * 80); // Price between $20 and $100
    const revenue = quantity * unitPrice;
    
    return {
      id: `prod-${index + 1}`,
      name: product.name,
      quantity,
      revenue,
      category: product.category,
      percentageOfTotal: 0, // Will be calculated below
    };
  });
  
  // Sort products by the requested metric
  products.sort((a, b) => 
    sortBy === 'quantity' 
      ? b.quantity - a.quantity 
      : b.revenue - a.revenue
  );
  
  // Calculate totals
  const totalRevenue = products.reduce((sum, product) => sum + product.revenue, 0);
  const totalQuantity = products.reduce((sum, product) => sum + product.quantity, 0);
  
  // Calculate percentage of total
  products.forEach(product => {
    product.percentageOfTotal = sortBy === 'quantity'
      ? (product.quantity / totalQuantity) * 100
      : (product.revenue / totalRevenue) * 100;
  });
  
  return {
    products,
    totalRevenue,
    totalQuantity,
    startDate: from,
    endDate: to,
  };
}

/**
 * Hook to calculate sales trends comparing two periods
 */
export function useSalesTrend(
  currentPeriod: '7days' | '30days' | '90days' = '30days',
  options: { 
    useRealData?: boolean; 
    enabled?: boolean;
    warehouseId?: string | null;
  } = {}
) {
  const { currentTenant } = useTenant();
  const { 
    useRealData = false, 
    enabled = true,
    warehouseId = null
  } = options;

  return useQuery({
    queryKey: ['salesTrend', currentPeriod, useRealData, currentTenant.id, warehouseId],
    queryFn: async () => {
      if (useRealData) {
        try {
          // Calculate date ranges for current and previous periods
          const today = new Date();
          const currentEndDate = new Date(today);
          const currentStartDate = new Date(today);
          const previousStartDate = new Date(today);
          const previousEndDate = new Date(today);
          
          let days: number;
          
          switch (currentPeriod) {
            case '7days':
              days = 7;
              break;
            case '30days':
              days = 30;
              break;
            case '90days':
              days = 90;
              break;
            default:
              days = 30;
          }
          
          // Set date ranges
          currentStartDate.setDate(today.getDate() - days);
          previousStartDate.setDate(today.getDate() - (days * 2));
          previousEndDate.setDate(today.getDate() - (days + 1));
          
          // Format dates for API requests
          const currentStart = currentStartDate.toISOString().split('T')[0];
          const currentEnd = currentEndDate.toISOString().split('T')[0];
          const previousStart = previousStartDate.toISOString().split('T')[0];
          const previousEnd = previousEndDate.toISOString().split('T')[0];
          
          // Fetch sales data for both periods with warehouse filter if provided
          const [currentSales, previousSales] = await Promise.all([
            prohandelClient.getSales({ 
              from: currentStart, 
              to: currentEnd,
              ...(warehouseId ? { location_id: warehouseId } : {})
            }),
            prohandelClient.getSales({ 
              from: previousStart, 
              to: previousEnd,
              ...(warehouseId ? { location_id: warehouseId } : {})
            })
          ]);
          
          // Calculate totals
          const currentTotalRevenue = currentSales.data.reduce(
            (sum: number, sale: any) => sum + (sale.total_amount || 0), 
            0
          );
          
          const previousTotalRevenue = previousSales.data.reduce(
            (sum: number, sale: any) => sum + (sale.total_amount || 0), 
            0
          );
          
          const currentOrderCount = currentSales.data.length;
          const previousOrderCount = previousSales.data.length;
          
          // Calculate percent changes
          const revenuePercentChange = previousTotalRevenue === 0 
            ? 100 
            : ((currentTotalRevenue - previousTotalRevenue) / previousTotalRevenue) * 100;
            
          const orderCountPercentChange = previousOrderCount === 0 
            ? 100 
            : ((currentOrderCount - previousOrderCount) / previousOrderCount) * 100;
          
          return {
            currentPeriod: {
              startDate: currentStart,
              endDate: currentEnd,
              totalRevenue: currentTotalRevenue,
              orderCount: currentOrderCount,
            },
            previousPeriod: {
              startDate: previousStart,
              endDate: previousEnd,
              totalRevenue: previousTotalRevenue,
              orderCount: previousOrderCount,
            },
            changes: {
              revenue: revenuePercentChange,
              orderCount: orderCountPercentChange,
            },
            periodName: getPeriodName(currentPeriod),
          };
        } catch (error) {
          console.error('Error fetching sales trend data:', error);
          // Fallback to mock data
          return getMockSalesTrend(currentPeriod);
        }
      } else {
        // Use mock data
        return getMockSalesTrend(currentPeriod);
      }
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Generate mock sales trend data for development
 */
function getMockSalesTrend(period: '7days' | '30days' | '90days'): any {
  const today = new Date();
  const currentEndDate = today.toISOString().split('T')[0];
  
  let days: number;
  let periodName: string;
  
  switch (period) {
    case '7days':
      days = 7;
      periodName = 'week';
      break;
    case '30days':
      days = 30;
      periodName = 'month';
      break;
    case '90days':
      days = 90;
      periodName = 'quarter';
      break;
    default:
      days = 30;
      periodName = 'month';
  }
  
  // Generate date strings
  const currentStartDate = new Date(today);
  currentStartDate.setDate(today.getDate() - days);
  
  const previousEndDate = new Date(currentStartDate);
  previousEndDate.setDate(previousEndDate.getDate() - 1);
  
  const previousStartDate = new Date(previousEndDate);
  previousStartDate.setDate(previousEndDate.getDate() - days);
  
  // Generate random trend data with realistic changes
  const previousTotalRevenue = Math.round(50000 + Math.random() * 30000);
  const previousOrderCount = Math.round(500 + Math.random() * 300);
  
  // Generate change percentages between -20% and +30%
  const revenueChangePercent = Math.round((Math.random() * 50) - 20);
  const orderCountChangePercent = Math.round((Math.random() * 50) - 20);
  
  // Calculate current period values based on change percentage
  const currentTotalRevenue = Math.round(
    previousTotalRevenue * (1 + (revenueChangePercent / 100))
  );
  
  const currentOrderCount = Math.round(
    previousOrderCount * (1 + (orderCountChangePercent / 100))
  );
  
  return {
    currentPeriod: {
      startDate: currentStartDate.toISOString().split('T')[0],
      endDate: currentEndDate,
      totalRevenue: currentTotalRevenue,
      orderCount: currentOrderCount,
    },
    previousPeriod: {
      startDate: previousStartDate.toISOString().split('T')[0],
      endDate: previousEndDate.toISOString().split('T')[0],
      totalRevenue: previousTotalRevenue,
      orderCount: previousOrderCount,
    },
    changes: {
      revenue: revenueChangePercent,
      orderCount: orderCountChangePercent,
    },
    periodName,
  };
}

/**
 * Get a human-readable period name
 */
function getPeriodName(period: '7days' | '30days' | '90days'): string {
  switch (period) {
    case '7days':
      return 'week';
    case '30days':
      return 'month';
    case '90days':
      return 'quarter';
    default:
      return 'period';
  }
}
