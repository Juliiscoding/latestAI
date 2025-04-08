/**
 * ProHandel Mock Data
 * 
 * This file contains mock data for when real ProHandel API access is not available or desired.
 * Used for development, testing, and as a fallback when API calls fail.
 */

// Mock warehouses data
export const warehouses = [
  {
    id: '1',
    name: 'Hauptlager Berlin',
    description: 'Hauptlager für die Region Berlin und Brandenburg',
    address: 'Berlinerstraße 123, 10115 Berlin',
    active: true,
    isWebshop: false
  },
  {
    id: '2',
    name: 'Webshop Lager',
    description: 'Zentrallager für Online-Bestellungen',
    address: 'Hamburgallee 45, 20095 Hamburg',
    active: true,
    isWebshop: true
  },
  {
    id: '3',
    name: 'Filiallager München',
    description: 'Lager für die Filiale München',
    address: 'Münchnerstraße 67, 80331 München',
    active: true,
    isWebshop: false
  }
];

// Mock stockout risks data
export const stockoutRisks = [
  {
    id: '101',
    productId: '1001',
    name: 'Premium Bohrmaschine',
    sku: 'BM-1001',
    categoryId: '10',
    categoryName: 'Elektrowerkzeuge',
    stockLevel: 5,
    reorderPoint: 10,
    riskLevel: 'high',
    lastRestockDate: '2023-05-15',
    averageDailySales: 1.2,
    daysUntilStockout: 4
  },
  {
    id: '102',
    productId: '1002',
    name: 'Sicherheitshandschuhe',
    sku: 'SH-1002',
    categoryId: '20',
    categoryName: 'Arbeitsschutz',
    stockLevel: 8,
    reorderPoint: 15,
    riskLevel: 'medium',
    lastRestockDate: '2023-05-20',
    averageDailySales: 0.8,
    daysUntilStockout: 10
  },
  {
    id: '103',
    productId: '1003',
    name: 'Schraubendreher-Set',
    sku: 'SS-1003',
    categoryId: '30',
    categoryName: 'Handwerkzeuge',
    stockLevel: 2,
    reorderPoint: 8,
    riskLevel: 'critical',
    lastRestockDate: '2023-05-10',
    averageDailySales: 1.5,
    daysUntilStockout: 1
  }
];

// Mock sales data
export const sales = [
  {
    id: '5001',
    date: '2023-06-01',
    warehouseId: '1',
    customerId: '2001',
    totalAmount: 567.89,
    items: [
      {
        productId: '1001',
        name: 'Premium Bohrmaschine',
        quantity: 1,
        unitPrice: 299.99,
        categoryId: '10',
        categoryName: 'Elektrowerkzeuge'
      },
      {
        productId: '1002',
        name: 'Sicherheitshandschuhe',
        quantity: 2,
        unitPrice: 29.95,
        categoryId: '20',
        categoryName: 'Arbeitsschutz'
      }
    ]
  },
  {
    id: '5002',
    date: '2023-06-02',
    warehouseId: '1',
    customerId: '2002',
    totalAmount: 128.75,
    items: [
      {
        productId: '1003',
        name: 'Schraubendreher-Set',
        quantity: 1,
        unitPrice: 89.99,
        categoryId: '30',
        categoryName: 'Handwerkzeuge'
      }
    ]
  },
  {
    id: '5003',
    date: '2023-06-03',
    warehouseId: '2',
    customerId: '2003',
    totalAmount: 712.50,
    items: [
      {
        productId: '1001',
        name: 'Premium Bohrmaschine',
        quantity: 2,
        unitPrice: 299.99,
        categoryId: '10',
        categoryName: 'Elektrowerkzeuge'
      },
      {
        productId: '1004',
        name: 'Arbeitsleuchte',
        quantity: 1,
        unitPrice: 112.52,
        categoryId: '40',
        categoryName: 'Beleuchtung'
      }
    ]
  }
];

// Mock inventory data
export const inventory = [
  {
    categoryId: '10',
    categoryName: 'Elektrowerkzeuge',
    productCount: 25,
    inventoryValue: 12500.50,
    lowStockCount: 5,
    outOfStockCount: 2
  },
  {
    categoryId: '20',
    categoryName: 'Arbeitsschutz',
    productCount: 40,
    inventoryValue: 3800.75,
    lowStockCount: 8,
    outOfStockCount: 0
  },
  {
    categoryId: '30',
    categoryName: 'Handwerkzeuge',
    productCount: 60,
    inventoryValue: 8500.25,
    lowStockCount: 4,
    outOfStockCount: 1
  },
  {
    categoryId: '40',
    categoryName: 'Beleuchtung',
    productCount: 15,
    inventoryValue: 2500.00,
    lowStockCount: 3,
    outOfStockCount: 0
  }
];

// Mock AI context data
export const aiContext = {
  salesTrends: {
    last7d: 7890.50,
    last30d: 32450.75,
    last90d: 98670.25,
    growthRate: 12.5,
    segments: [
      {
        categoryId: '10',
        name: 'Elektrowerkzeuge',
        percentOfTotal: 45.8,
        growth: 15.3
      },
      {
        categoryId: '20',
        name: 'Arbeitsschutz',
        percentOfTotal: 15.2,
        growth: 8.7
      },
      {
        categoryId: '30',
        name: 'Handwerkzeuge',
        percentOfTotal: 25.5,
        growth: 10.1
      },
      {
        categoryId: '40',
        name: 'Beleuchtung',
        percentOfTotal: 13.5,
        growth: 5.8
      }
    ]
  },
  inventoryHealth: {
    stockouts: 3,
    atRisk: 17,
    stable: 145,
    riskItems: [
      {
        productId: '1001',
        name: 'Premium Bohrmaschine',
        stockLevel: 5,
        riskLevel: 'high',
        daysUntilStockout: 4
      },
      {
        productId: '1003',
        name: 'Schraubendreher-Set',
        stockLevel: 2,
        riskLevel: 'critical',
        daysUntilStockout: 1
      }
    ]
  },
  productInsights: {
    topProducts: [
      {
        productId: '1001',
        name: 'Premium Bohrmaschine',
        revenue: 8999.70,
        growth: 25.7
      },
      {
        productId: '1005',
        name: 'Akkuschrauber',
        revenue: 6540.45,
        growth: 18.3
      },
      {
        productId: '1003',
        name: 'Schraubendreher-Set',
        revenue: 5399.40,
        growth: 12.4
      }
    ],
    underperformers: [
      {
        productId: '1008',
        name: 'Fliesenkleber',
        revenue: 890.25,
        growth: -12.8
      },
      {
        productId: '1010',
        name: 'Arbeitshandschuhe Basic',
        revenue: 945.00,
        growth: -8.5
      }
    ]
  }
};
