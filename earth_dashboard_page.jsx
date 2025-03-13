/**
 * Earth Module Dashboard Page
 * 
 * This is the main dashboard for the Earth module, displaying key business metrics,
 * insights, and recommendations from Snowflake analytics views.
 */

import React, { useState } from 'react';
import { useQuery, gql } from '@apollo/client';
import {
  Box,
  Flex,
  Grid,
  GridItem,
  Heading,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  StatGroup,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Stack,
  StackDivider,
  Badge,
  Button,
  Icon,
  Divider,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  Select,
  HStack,
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
} from 'react-icons/fi';
import EarthDashboardLayout from '../components/earth/EarthDashboardLayout';
import { LineChart, BarChart, PieChart } from '../components/earth/charts';
import { RecommendationCard } from '../components/earth/recommendations';

// GraphQL queries
const GET_BUSINESS_DASHBOARD = gql`
  query GetBusinessDashboard {
    businessDashboard {
      totalSales {
        value
        comparisonValue
        percentChange
        trendDirection
        timePeriod
      }
      totalOrders {
        value
        comparisonValue
        percentChange
        trendDirection
        timePeriod
      }
      averageOrderValue {
        value
        comparisonValue
        percentChange
        trendDirection
        timePeriod
      }
      customerCount {
        value
        comparisonValue
        percentChange
        trendDirection
        timePeriod
      }
      inventoryValue {
        value
        comparisonValue
        percentChange
        trendDirection
        timePeriod
      }
      topSellingProduct
      topSellingCategory
    }
  }
`;

const GET_DAILY_SALES = gql`
  query GetDailySales($dateRange: DateRangeInput!) {
    dailySalesSummary(dateRange: $dateRange) {
      date
      totalSales
      totalOrders
      averageOrderValue
      totalUnitsSold
      totalUniqueCustomers
    }
  }
`;

const GET_INVENTORY_RECOMMENDATIONS = gql`
  query GetInventoryRecommendations {
    inventoryRecommendations {
      productId
      productName
      currentStock
      reorderPoint
      daysOfSupply
      recommendationType
      recommendationText
      recommendedActionValue
    }
  }
`;

export default function EarthDashboard() {
  // Time period selection
  const [timePeriod, setTimePeriod] = useState('30days');
  
  // Calculate date range based on selected time period
  const getDateRange = () => {
    const endDate = new Date();
    let startDate = new Date();
    
    switch (timePeriod) {
      case '7days':
        startDate.setDate(endDate.getDate() - 7);
        break;
      case '30days':
        startDate.setDate(endDate.getDate() - 30);
        break;
      case '90days':
        startDate.setDate(endDate.getDate() - 90);
        break;
      case 'year':
        startDate.setFullYear(endDate.getFullYear() - 1);
        break;
      default:
        startDate.setDate(endDate.getDate() - 30);
    }
    
    return {
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0]
    };
  };
  
  // Fetch dashboard data
  const { 
    loading: dashboardLoading, 
    error: dashboardError, 
    data: dashboardData 
  } = useQuery(GET_BUSINESS_DASHBOARD);
  
  // Fetch sales data
  const { 
    loading: salesLoading, 
    error: salesError, 
    data: salesData 
  } = useQuery(GET_DAILY_SALES, {
    variables: { dateRange: getDateRange() }
  });
  
  // Fetch recommendations
  const { 
    loading: recommendationsLoading, 
    error: recommendationsError, 
    data: recommendationsData 
  } = useQuery(GET_INVENTORY_RECOMMENDATIONS);
  
  // Loading state
  if (dashboardLoading || salesLoading || recommendationsLoading) {
    return (
      <EarthDashboardLayout>
        <Flex justify="center" align="center" height="80vh">
          <Spinner size="xl" color="blue.500" thickness="4px" />
        </Flex>
      </EarthDashboardLayout>
    );
  }
  
  // Error state
  if (dashboardError || salesError || recommendationsError) {
    return (
      <EarthDashboardLayout>
        <Alert status="error" variant="solid" borderRadius="md">
          <AlertIcon />
          An error occurred while loading the dashboard data. Please try again later.
        </Alert>
      </EarthDashboardLayout>
    );
  }
  
  // Extract dashboard data
  const dashboard = dashboardData?.businessDashboard || {};
  
  // Prepare sales chart data
  const salesChartData = salesData?.dailySalesSummary?.map(item => ({
    date: new Date(item.date).toLocaleDateString(),
    sales: item.totalSales,
    orders: item.totalOrders
  })) || [];
  
  // Get top recommendations
  const topRecommendations = recommendationsData?.inventoryRecommendations?.slice(0, 3) || [];
  
  return (
    <EarthDashboardLayout>
      {/* Dashboard Header */}
      <Flex justify="space-between" align="center" mb={6}>
        <Box>
          <Heading size="lg">Business Dashboard</Heading>
          <Text color="gray.500">Real-time insights from your business data</Text>
        </Box>
        <HStack spacing={4}>
          <Select 
            value={timePeriod} 
            onChange={(e) => setTimePeriod(e.target.value)}
            width="200px"
          >
            <option value="7days">Last 7 Days</option>
            <option value="30days">Last 30 Days</option>
            <option value="90days">Last 90 Days</option>
            <option value="year">Last Year</option>
          </Select>
          <Button leftIcon={<FiCalendar />} colorScheme="blue">
            Custom Range
          </Button>
        </HStack>
      </Flex>
      
      {/* Key Metrics */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 5 }} spacing={6} mb={8}>
        {/* Total Sales */}
        <MetricCard
          title="Total Sales"
          value={dashboard.totalSales?.value || 0}
          format="currency"
          change={dashboard.totalSales?.percentChange || 0}
          period={dashboard.totalSales?.timePeriod || ""}
          icon={FiDollarSign}
          colorScheme="green"
        />
        
        {/* Total Orders */}
        <MetricCard
          title="Total Orders"
          value={dashboard.totalOrders?.value || 0}
          format="number"
          change={dashboard.totalOrders?.percentChange || 0}
          period={dashboard.totalOrders?.timePeriod || ""}
          icon={FiShoppingBag}
          colorScheme="blue"
        />
        
        {/* Average Order Value */}
        <MetricCard
          title="Avg. Order Value"
          value={dashboard.averageOrderValue?.value || 0}
          format="currency"
          change={dashboard.averageOrderValue?.percentChange || 0}
          period={dashboard.averageOrderValue?.timePeriod || ""}
          icon={FiBarChart2}
          colorScheme="purple"
        />
        
        {/* Customer Count */}
        <MetricCard
          title="Customers"
          value={dashboard.customerCount?.value || 0}
          format="number"
          change={dashboard.customerCount?.percentChange || 0}
          period={dashboard.customerCount?.timePeriod || ""}
          icon={FiUsers}
          colorScheme="orange"
        />
        
        {/* Inventory Value */}
        <MetricCard
          title="Inventory Value"
          value={dashboard.inventoryValue?.value || 0}
          format="currency"
          change={dashboard.inventoryValue?.percentChange || 0}
          period={dashboard.inventoryValue?.timePeriod || ""}
          icon={FiPackage}
          colorScheme="cyan"
        />
      </SimpleGrid>
      
      {/* Charts and Insights */}
      <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6} mb={8}>
        {/* Sales Trend Chart */}
        <GridItem>
          <Card>
            <CardHeader>
              <Heading size="md">Sales Trend</Heading>
            </CardHeader>
            <CardBody>
              {salesChartData.length > 0 ? (
                <Box height="300px">
                  <LineChart 
                    data={salesChartData} 
                    xKey="date" 
                    yKeys={["sales"]} 
                    colors={["#3182CE"]} 
                  />
                </Box>
              ) : (
                <Text>No sales data available for the selected period.</Text>
              )}
            </CardBody>
          </Card>
        </GridItem>
        
        {/* Top Insights */}
        <GridItem>
          <Card height="100%">
            <CardHeader>
              <Heading size="md">Top Insights</Heading>
            </CardHeader>
            <CardBody>
              <Stack divider={<StackDivider />} spacing={4}>
                <Box>
                  <HStack>
                    <Icon as={FiTrendingUp} color="green.500" />
                    <Text fontWeight="bold">Top Selling Product</Text>
                  </HStack>
                  <Text mt={1}>{dashboard.topSellingProduct || "No data available"}</Text>
                </Box>
                <Box>
                  <HStack>
                    <Icon as={FiBarChart2} color="blue.500" />
                    <Text fontWeight="bold">Top Category</Text>
                  </HStack>
                  <Text mt={1}>{dashboard.topSellingCategory || "No data available"}</Text>
                </Box>
                <Box>
                  <HStack>
                    <Icon as={FiUsers} color="purple.500" />
                    <Text fontWeight="bold">Customer Growth</Text>
                  </HStack>
                  <Text mt={1}>
                    {dashboard.customerCount?.percentChange > 0 
                      ? `Growing at ${dashboard.customerCount?.percentChange}% compared to previous period` 
                      : "No growth in customer base"}
                  </Text>
                </Box>
              </Stack>
            </CardBody>
          </Card>
        </GridItem>
      </Grid>
      
      {/* Recommendations */}
      <Box mb={8}>
        <Flex justify="space-between" align="center" mb={4}>
          <Heading size="md">Recommendations</Heading>
          <Button variant="outline" colorScheme="blue" size="sm">
            View All
          </Button>
        </Flex>
        
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          {topRecommendations.length > 0 ? (
            topRecommendations.map((rec, index) => (
              <Card key={index} borderLeft="4px solid" borderLeftColor={rec.recommendationType === "RESTOCK" ? "red.500" : "orange.500"}>
                <CardHeader pb={0}>
                  <Flex justify="space-between" align="center">
                    <Heading size="sm">{rec.productName}</Heading>
                    <Badge colorScheme={rec.recommendationType === "RESTOCK" ? "red" : "orange"}>
                      {rec.recommendationType}
                    </Badge>
                  </Flex>
                </CardHeader>
                <CardBody>
                  <Text fontSize="sm">{rec.recommendationText}</Text>
                  <HStack mt={2}>
                    <Text fontWeight="bold" fontSize="sm">Action:</Text>
                    <Text fontSize="sm">
                      {rec.recommendationType === "RESTOCK" 
                        ? `Order ${rec.recommendedActionValue} units` 
                        : `Reduce by ${rec.recommendedActionValue} units`}
                    </Text>
                  </HStack>
                </CardBody>
                <CardFooter pt={0}>
                  <Button size="sm" width="full" colorScheme={rec.recommendationType === "RESTOCK" ? "red" : "orange"} variant="outline">
                    Take Action
                  </Button>
                </CardFooter>
              </Card>
            ))
          ) : (
            <Text>No recommendations available at this time.</Text>
          )}
        </SimpleGrid>
      </Box>
    </EarthDashboardLayout>
  );
}

// Metric Card Component
function MetricCard({ title, value, format, change, period, icon, colorScheme }) {
  const bgColor = useColorModeValue('white', 'gray.700');
  const iconBgColor = useColorModeValue(`${colorScheme}.50`, `${colorScheme}.900`);
  const iconColor = useColorModeValue(`${colorScheme}.500`, `${colorScheme}.200`);
  
  // Format value based on type
  const formattedValue = format === 'currency'
    ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
    : new Intl.NumberFormat('en-US').format(value);
  
  return (
    <Card bg={bgColor}>
      <CardBody>
        <Flex justify="space-between" align="flex-start">
          <Box>
            <Text color="gray.500" fontSize="sm">{title}</Text>
            <Text fontSize="2xl" fontWeight="bold" mt={1}>
              {formattedValue}
            </Text>
            <Flex align="center" mt={2}>
              <StatArrow type={change >= 0 ? 'increase' : 'decrease'} />
              <Text 
                fontSize="sm" 
                color={change >= 0 ? 'green.500' : 'red.500'}
              >
                {Math.abs(change)}%
              </Text>
              <Text fontSize="sm" color="gray.500" ml={1}>
                vs {period}
              </Text>
            </Flex>
          </Box>
          <Box 
            p={2} 
            borderRadius="md" 
            bg={iconBgColor}
          >
            <Icon as={icon} boxSize={6} color={iconColor} />
          </Box>
        </Flex>
      </CardBody>
    </Card>
  );
}

// This page requires authentication
EarthDashboard.auth = true;
