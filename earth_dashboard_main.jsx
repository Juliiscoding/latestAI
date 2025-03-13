/**
 * Earth Module Main Dashboard
 * 
 * This component implements the main dashboard for the Earth module, integrating
 * shadcn/ui charts with the recommendation engine to provide a comprehensive
 * business intelligence solution.
 */

import React, { useState, useEffect } from 'react';
import { useQuery, gql } from '@apollo/client';
import {
  Box,
  Flex,
  Grid,
  GridItem,
  Heading,
  Text,
  Button,
  Icon,
  Select,
  HStack,
  VStack,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Badge,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Divider,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
} from '@chakra-ui/react';
import {
  FiTrendingUp,
  FiTrendingDown,
  FiAlertCircle,
  FiCheckCircle,
  FiBarChart2,
  FiUsers,
  FiPackage,
  FiShoppingBag,
  FiDollarSign,
  FiCalendar,
  FiArrowRight,
  FiExternalLink,
  FiInfo,
  FiStar,
  FiFilter,
  FiRefreshCw,
  FiChevronDown,
  FiSettings,
  FiDownload,
  FiPrinter,
  FiShare2,
  FiClock,
  FiSliders,
} from 'react-icons/fi';

// Import chart components
import {
  SalesTrendChart,
  SalesComparisonChart,
  CustomerDistributionChart,
  ProductPerformanceRadarChart,
  MultiProductRadarChart,
  MetricGaugeChart,
  InteractiveDailySalesChart,
  MultiMetricDashboardCard,
} from './earth_shadcn_charts';

// Import recommendation components
import {
  RecommendationCard,
  RecommendationActionModal,
  RecommendationsDashboard,
  InventoryRecommendations,
} from './earth_recommendation_engine';

// GraphQL queries
const GET_DASHBOARD_DATA = gql`
  query GetDashboardData($timeRange: String, $shopId: ID) {
    dailySalesSummary(timeRange: $timeRange, shopId: $shopId) {
      date
      totalSales
      totalOrders
      averageOrderValue
      comparisonSales
      comparisonOrders
    }
    customerInsights(timeRange: $timeRange, shopId: $shopId) {
      segment
      count
      revenue
      frequency
    }
    productPerformance(timeRange: $timeRange, shopId: $shopId) {
      productId
      productName
      sales
      quantity
      profit
      returnRate
      rating
    }
    shopPerformance(timeRange: $timeRange) {
      shopId
      shopName
      totalSales
      totalOrders
      customerCount
      averageOrderValue
      yearOverYearGrowth
    }
    topRecommendations(limit: 3) {
      id
      type
      title
      description
      impact
      confidence
    }
  }
`;

/**
 * Dashboard Header Component
 * 
 * Displays the dashboard title, time range selector, and action buttons.
 */
const DashboardHeader = ({ timeRange, setTimeRange, onRefresh }) => {
  return (
    <Flex 
      justify="space-between" 
      align="center" 
      mb={6}
      pb={4}
      borderBottomWidth="1px"
      borderBottomColor={useColorModeValue("gray.200", "gray.700")}
    >
      <Box>
        <Heading size="lg">Earth Business Intelligence</Heading>
        <Text color="gray.500">Real-time insights from your Snowflake data</Text>
      </Box>
      
      <HStack spacing={4}>
        <Select 
          value={timeRange} 
          onChange={(e) => setTimeRange(e.target.value)}
          width="auto"
          size="sm"
        >
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="90d">Last 90 Days</option>
          <option value="ytd">Year to Date</option>
          <option value="1y">Last Year</option>
        </Select>
        
        <Menu>
          <MenuButton as={Button} rightIcon={<FiChevronDown />} size="sm" variant="outline">
            <Icon as={FiDownload} mr={2} />
            Export
          </MenuButton>
          <MenuList>
            <MenuItem icon={<FiDownload />}>Export as PDF</MenuItem>
            <MenuItem icon={<FiDownload />}>Export as Excel</MenuItem>
            <MenuItem icon={<FiPrinter />}>Print Dashboard</MenuItem>
            <MenuItem icon={<FiShare2 />}>Share Dashboard</MenuItem>
          </MenuList>
        </Menu>
        
        <Button 
          leftIcon={<FiRefreshCw />} 
          colorScheme="blue" 
          size="sm"
          onClick={onRefresh}
        >
          Refresh
        </Button>
      </HStack>
    </Flex>
  );
};

/**
 * Key Metrics Component
 * 
 * Displays key business metrics in a grid of stat cards.
 */
const KeyMetrics = ({ data, isLoading }) => {
  if (isLoading) {
    return (
      <Grid templateColumns={{ base: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }} gap={6} mb={8}>
        {[...Array(4)].map((_, i) => (
          <Box key={i} p={5} shadow="md" borderWidth="1px" borderRadius="md">
            <Spinner size="sm" />
          </Box>
        ))}
      </Grid>
    );
  }
  
  // Calculate aggregated metrics
  const totalSales = data?.dailySalesSummary?.reduce((sum, day) => sum + day.totalSales, 0) || 0;
  const totalOrders = data?.dailySalesSummary?.reduce((sum, day) => sum + day.totalOrders, 0) || 0;
  const avgOrderValue = totalOrders > 0 ? totalSales / totalOrders : 0;
  
  // Calculate comparison metrics
  const comparisonSales = data?.dailySalesSummary?.reduce((sum, day) => sum + (day.comparisonSales || 0), 0) || 0;
  const salesGrowth = comparisonSales > 0 ? ((totalSales - comparisonSales) / comparisonSales) * 100 : 0;
  
  const comparisonOrders = data?.dailySalesSummary?.reduce((sum, day) => sum + (day.comparisonOrders || 0), 0) || 0;
  const ordersGrowth = comparisonOrders > 0 ? ((totalOrders - comparisonOrders) / comparisonOrders) * 100 : 0;
  
  // Customer metrics
  const customerCount = data?.customerInsights?.reduce((sum, segment) => sum + segment.count, 0) || 0;
  
  return (
    <Grid templateColumns={{ base: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }} gap={6} mb={8}>
      <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" bg={useColorModeValue("white", "gray.700")}>
        <Stat>
          <StatLabel>Total Sales</StatLabel>
          <StatNumber>${totalSales.toLocaleString()}</StatNumber>
          <StatHelpText>
            <StatArrow type={salesGrowth >= 0 ? "increase" : "decrease"} />
            {Math.abs(salesGrowth).toFixed(1)}%
          </StatHelpText>
        </Stat>
      </Box>
      
      <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" bg={useColorModeValue("white", "gray.700")}>
        <Stat>
          <StatLabel>Total Orders</StatLabel>
          <StatNumber>{totalOrders.toLocaleString()}</StatNumber>
          <StatHelpText>
            <StatArrow type={ordersGrowth >= 0 ? "increase" : "decrease"} />
            {Math.abs(ordersGrowth).toFixed(1)}%
          </StatHelpText>
        </Stat>
      </Box>
      
      <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" bg={useColorModeValue("white", "gray.700")}>
        <Stat>
          <StatLabel>Average Order Value</StatLabel>
          <StatNumber>${avgOrderValue.toFixed(2)}</StatNumber>
          <StatHelpText>
            <Icon as={FiUsers} mr={1} />
            Per transaction
          </StatHelpText>
        </Stat>
      </Box>
      
      <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" bg={useColorModeValue("white", "gray.700")}>
        <Stat>
          <StatLabel>Total Customers</StatLabel>
          <StatNumber>{customerCount.toLocaleString()}</StatNumber>
          <StatHelpText>
            <Icon as={FiUsers} mr={1} />
            Active buyers
          </StatHelpText>
        </Stat>
      </Box>
    </Grid>
  );
};

/**
 * Dashboard Charts Section
 * 
 * Displays the main charts for the dashboard.
 */
const DashboardCharts = ({ data, isLoading }) => {
  if (isLoading) {
    return (
      <Flex justify="center" align="center" height="300px">
        <Spinner size="xl" thickness="4px" color="blue.500" />
      </Flex>
    );
  }
  
  // Format data for sales trend chart
  const salesTrendData = data?.dailySalesSummary?.map(day => ({
    date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    sales: day.totalSales,
  })) || [];
  
  // Format data for sales comparison chart
  const salesComparisonData = data?.dailySalesSummary?.map(day => ({
    date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    current: day.totalSales,
    previous: day.comparisonSales || 0,
  })) || [];
  
  // Format data for customer distribution chart
  const customerDistributionData = data?.customerInsights?.map(segment => ({
    name: segment.segment,
    value: segment.count,
  })) || [];
  
  // Format data for product performance radar chart
  const productPerformanceData = data?.productPerformance?.slice(0, 5).map(product => ({
    product: product.productName,
    sales: product.sales / 1000, // Scale down for better visualization
    quantity: product.quantity / 10, // Scale down for better visualization
    profit: product.profit / 100, // Scale down for better visualization
    rating: product.rating * 20, // Scale up (assuming rating is 0-5, convert to 0-100)
    returnRate: 100 - product.returnRate * 100, // Invert and scale (lower is better)
  })) || [];
  
  return (
    <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6} mb={8}>
      <GridItem>
        <SalesTrendChart 
          data={salesTrendData}
          title="Sales Trend"
          description="Daily sales performance over time"
        />
      </GridItem>
      
      <GridItem>
        <CustomerDistributionChart 
          data={customerDistributionData}
          title="Customer Segments"
          description="Distribution of customers by segment"
        />
      </GridItem>
      
      <GridItem colSpan={{ base: 1, lg: 2 }}>
        <SalesComparisonChart 
          data={salesComparisonData}
          categories={["current", "previous"]}
          title="Period Comparison"
          description="Current vs previous period sales"
        />
      </GridItem>
      
      <GridItem colSpan={{ base: 1, lg: 2 }}>
        <ProductPerformanceRadarChart 
          data={productPerformanceData}
          title="Top Product Performance"
          description="Multi-dimensional analysis of top 5 products"
        />
      </GridItem>
    </Grid>
  );
};

/**
 * Top Recommendations Section
 * 
 * Displays the top recommendations from the recommendation engine.
 */
const TopRecommendations = ({ recommendations, isLoading, onViewAll }) => {
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const actionModal = useDisclosure();
  
  // Handle recommendation action
  const handleAction = (recommendation) => {
    setSelectedRecommendation(recommendation);
    actionModal.onOpen();
  };
  
  if (isLoading) {
    return (
      <Box mb={8}>
        <Flex justify="space-between" align="center" mb={4}>
          <Heading size="md">Top Recommendations</Heading>
        </Flex>
        <Flex justify="center" align="center" height="200px">
          <Spinner size="lg" thickness="3px" color="blue.500" />
        </Flex>
      </Box>
    );
  }
  
  if (!recommendations || recommendations.length === 0) {
    return (
      <Box mb={8}>
        <Flex justify="space-between" align="center" mb={4}>
          <Heading size="md">Top Recommendations</Heading>
          <Button size="sm" variant="outline" onClick={onViewAll}>
            View All
          </Button>
        </Flex>
        <Box 
          textAlign="center" 
          p={6} 
          borderWidth="1px" 
          borderRadius="md"
          bg={useColorModeValue("white", "gray.700")}
        >
          <Icon as={FiCheckCircle} boxSize={10} color="green.500" mb={4} />
          <Heading size="sm" mb={2}>All Caught Up!</Heading>
          <Text color="gray.500">
            There are no recommendations at this time. Check back later for new insights.
          </Text>
        </Box>
      </Box>
    );
  }
  
  return (
    <Box mb={8}>
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="md">Top Recommendations</Heading>
        <Button size="sm" variant="outline" rightIcon={<FiArrowRight />} onClick={onViewAll}>
          View All
        </Button>
      </Flex>
      
      <Grid templateColumns={{ base: "1fr", md: "repeat(3, 1fr)" }} gap={6}>
        {recommendations.map((recommendation) => (
          <GridItem key={recommendation.id}>
            <RecommendationCard 
              recommendation={recommendation} 
              onAction={handleAction}
            />
          </GridItem>
        ))}
      </Grid>
      
      {/* Action Modal */}
      <RecommendationActionModal
        isOpen={actionModal.isOpen}
        onClose={actionModal.onClose}
        recommendation={selectedRecommendation}
      />
    </Box>
  );
};

/**
 * Main Dashboard Component
 * 
 * The main dashboard component that integrates all sections.
 */
export const EarthDashboard = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const recommendationsDrawer = useDisclosure();
  
  // Fetch dashboard data
  const { loading, error, data, refetch } = useQuery(GET_DASHBOARD_DATA, {
    variables: { timeRange },
  });
  
  // Handle refresh
  const handleRefresh = () => {
    refetch();
  };
  
  // Handle view all recommendations
  const handleViewAllRecommendations = () => {
    recommendationsDrawer.onOpen();
  };
  
  // Error state
  if (error) {
    return (
      <Alert status="error" variant="solid" borderRadius="md">
        <AlertIcon />
        An error occurred while loading dashboard data. Please try again later.
      </Alert>
    );
  }
  
  return (
    <Box p={6}>
      {/* Dashboard Header */}
      <DashboardHeader 
        timeRange={timeRange} 
        setTimeRange={setTimeRange} 
        onRefresh={handleRefresh}
      />
      
      {/* Key Metrics */}
      <KeyMetrics data={data} isLoading={loading} />
      
      {/* Dashboard Charts */}
      <DashboardCharts data={data} isLoading={loading} />
      
      {/* Top Recommendations */}
      <TopRecommendations 
        recommendations={data?.topRecommendations} 
        isLoading={loading}
        onViewAll={handleViewAllRecommendations}
      />
      
      {/* Recommendations Drawer */}
      <Drawer
        isOpen={recommendationsDrawer.isOpen}
        placement="right"
        onClose={recommendationsDrawer.onClose}
        size="xl"
      >
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">
            Business Recommendations
          </DrawerHeader>
          
          <DrawerBody p={4}>
            <Tabs variant="enclosed" colorScheme="blue">
              <TabList>
                <Tab>All Recommendations</Tab>
                <Tab>Inventory</Tab>
              </TabList>
              
              <TabPanels>
                <TabPanel px={0}>
                  <RecommendationsDashboard />
                </TabPanel>
                <TabPanel px={0}>
                  <InventoryRecommendations />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Box>
  );
};

export default EarthDashboard;
