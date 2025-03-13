/**
 * Earth Module Recommendation Engine
 * 
 * This component implements the AI-driven recommendation engine for the Earth module.
 * It processes data from Snowflake analytics views to generate actionable business insights.
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
  Badge,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Stack,
  Divider,
  HStack,
  VStack,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Select,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  Progress,
  Tooltip,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
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
  FiThumbsUp,
  FiThumbsDown,
  FiFilter,
  FiRefreshCw,
} from 'react-icons/fi';

// GraphQL query for recommendations
const GET_RECOMMENDATIONS = gql`
  query GetRecommendations($type: RecommendationType) {
    recommendations(type: $type) {
      id
      type
      title
      description
      impact
      confidence
      suggestedActions
      relatedEntityId
      relatedEntityType
    }
  }
`;

// GraphQL query for inventory recommendations
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

/**
 * Recommendation Card Component
 * 
 * Displays a single recommendation with actions and details.
 */
export const RecommendationCard = ({ recommendation, onAction }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  // Determine color scheme based on recommendation type
  const getColorScheme = (type) => {
    switch (type) {
      case 'INVENTORY_OPTIMIZATION':
        return 'blue';
      case 'CUSTOMER_TARGETING':
        return 'purple';
      case 'PRICING_STRATEGY':
        return 'green';
      case 'MARKETING_CAMPAIGN':
        return 'orange';
      case 'PRODUCT_BUNDLING':
        return 'teal';
      default:
        return 'gray';
    }
  };
  
  // Format impact and confidence as percentages
  const formatPercentage = (value) => {
    return `${Math.round(value * 100)}%`;
  };
  
  const colorScheme = getColorScheme(recommendation.type);
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue(`${colorScheme}.100`, `${colorScheme}.800`);
  
  return (
    <>
      <Card 
        bg={cardBg}
        borderLeft="4px solid" 
        borderLeftColor={`${colorScheme}.500`}
        boxShadow="sm"
        transition="all 0.2s"
        _hover={{ boxShadow: 'md', transform: 'translateY(-2px)' }}
      >
        <CardHeader pb={2}>
          <Flex justify="space-between" align="center">
            <HStack>
              <Badge colorScheme={colorScheme} fontSize="0.8em">
                {recommendation.type.replace(/_/g, ' ')}
              </Badge>
              {recommendation.impact >= 0.7 && (
                <Badge colorScheme="red">High Impact</Badge>
              )}
            </HStack>
            <Tooltip label="View details">
              <Button size="sm" variant="ghost" onClick={onOpen}>
                <Icon as={FiInfo} />
              </Button>
            </Tooltip>
          </Flex>
          <Heading size="md" mt={2}>{recommendation.title}</Heading>
        </CardHeader>
        
        <CardBody py={2}>
          <Text fontSize="sm" noOfLines={2}>
            {recommendation.description}
          </Text>
          
          <HStack mt={4} spacing={4}>
            <VStack align="flex-start" spacing={0}>
              <Text fontSize="xs" color="gray.500">Impact</Text>
              <HStack>
                <Progress 
                  value={recommendation.impact * 100} 
                  size="sm" 
                  colorScheme={colorScheme} 
                  borderRadius="full" 
                  width="80px"
                />
                <Text fontSize="sm" fontWeight="bold">
                  {formatPercentage(recommendation.impact)}
                </Text>
              </HStack>
            </VStack>
            
            <VStack align="flex-start" spacing={0}>
              <Text fontSize="xs" color="gray.500">Confidence</Text>
              <HStack>
                <Progress 
                  value={recommendation.confidence * 100} 
                  size="sm" 
                  colorScheme="gray" 
                  borderRadius="full" 
                  width="80px"
                />
                <Text fontSize="sm" fontWeight="bold">
                  {formatPercentage(recommendation.confidence)}
                </Text>
              </HStack>
            </VStack>
          </HStack>
        </CardBody>
        
        <CardFooter pt={0}>
          <Button 
            rightIcon={<FiArrowRight />} 
            colorScheme={colorScheme} 
            size="sm"
            onClick={() => onAction(recommendation)}
            width="full"
          >
            Take Action
          </Button>
        </CardFooter>
      </Card>
      
      {/* Recommendation Detail Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <HStack>
              <Badge colorScheme={colorScheme} fontSize="0.8em">
                {recommendation.type.replace(/_/g, ' ')}
              </Badge>
              <Text>{recommendation.title}</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            <Text mb={4}>{recommendation.description}</Text>
            
            <Heading size="sm" mb={2}>Suggested Actions</Heading>
            <VStack align="stretch" mb={4} spacing={2}>
              {recommendation.suggestedActions.map((action, index) => (
                <HStack key={index} p={2} bg="gray.50" borderRadius="md">
                  <Icon as={FiCheckCircle} color="green.500" />
                  <Text>{action}</Text>
                </HStack>
              ))}
            </VStack>
            
            <Grid templateColumns="repeat(2, 1fr)" gap={4} mb={4}>
              <GridItem>
                <Text fontSize="sm" color="gray.500">Impact</Text>
                <HStack>
                  <Progress 
                    value={recommendation.impact * 100} 
                    size="sm" 
                    colorScheme={colorScheme} 
                    borderRadius="full" 
                    width="full"
                  />
                  <Text fontSize="sm" fontWeight="bold" width="40px" textAlign="right">
                    {formatPercentage(recommendation.impact)}
                  </Text>
                </HStack>
              </GridItem>
              
              <GridItem>
                <Text fontSize="sm" color="gray.500">Confidence</Text>
                <HStack>
                  <Progress 
                    value={recommendation.confidence * 100} 
                    size="sm" 
                    colorScheme="gray" 
                    borderRadius="full" 
                    width="full"
                  />
                  <Text fontSize="sm" fontWeight="bold" width="40px" textAlign="right">
                    {formatPercentage(recommendation.confidence)}
                  </Text>
                </HStack>
              </GridItem>
            </Grid>
            
            {recommendation.relatedEntityId && (
              <HStack mt={4}>
                <Text fontSize="sm" color="gray.500">Related {recommendation.relatedEntityType}:</Text>
                <Text fontSize="sm" fontWeight="bold">{recommendation.relatedEntityId}</Text>
                <Button 
                  size="xs" 
                  variant="ghost" 
                  leftIcon={<FiExternalLink />}
                  as="a"
                  href={`/earth/${recommendation.relatedEntityType.toLowerCase()}s/${recommendation.relatedEntityId}`}
                >
                  View
                </Button>
              </HStack>
            )}
          </ModalBody>
          
          <ModalFooter>
            <HStack spacing={4}>
              <Button leftIcon={<FiThumbsDown />} variant="ghost" size="sm">
                Not Helpful
              </Button>
              <Button leftIcon={<FiThumbsUp />} variant="ghost" size="sm">
                Helpful
              </Button>
              <Button 
                rightIcon={<FiArrowRight />} 
                colorScheme={colorScheme}
                onClick={() => {
                  onAction(recommendation);
                  onClose();
                }}
              >
                Take Action
              </Button>
            </HStack>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

/**
 * Recommendation Action Modal Component
 * 
 * Modal for taking action on a recommendation.
 */
export const RecommendationActionModal = ({ 
  isOpen, 
  onClose, 
  recommendation,
  onActionComplete 
}) => {
  const [actionStatus, setActionStatus] = useState('pending'); // pending, processing, completed, failed
  
  // Simulate action processing
  const handleAction = () => {
    setActionStatus('processing');
    
    // Simulate API call with timeout
    setTimeout(() => {
      setActionStatus('completed');
      
      // Notify parent component
      if (onActionComplete) {
        onActionComplete(recommendation);
      }
    }, 2000);
  };
  
  // Determine color scheme based on recommendation type
  const getColorScheme = (type) => {
    switch (type) {
      case 'INVENTORY_OPTIMIZATION':
        return 'blue';
      case 'CUSTOMER_TARGETING':
        return 'purple';
      case 'PRICING_STRATEGY':
        return 'green';
      case 'MARKETING_CAMPAIGN':
        return 'orange';
      case 'PRODUCT_BUNDLING':
        return 'teal';
      default:
        return 'gray';
    }
  };
  
  const colorScheme = getColorScheme(recommendation?.type || '');
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          Take Action: {recommendation?.title}
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          {actionStatus === 'pending' && (
            <>
              <Text mb={4}>{recommendation?.description}</Text>
              
              <Heading size="sm" mb={2}>Actions to Take</Heading>
              <VStack align="stretch" mb={4} spacing={2}>
                {recommendation?.suggestedActions.map((action, index) => (
                  <HStack key={index} p={3} bg="gray.50" borderRadius="md">
                    <Icon as={FiCheckCircle} color="green.500" />
                    <Text>{action}</Text>
                  </HStack>
                ))}
              </VStack>
              
              <Alert status="info" borderRadius="md" mb={4}>
                <AlertIcon />
                Implementing this recommendation could lead to an estimated impact of {Math.round(recommendation?.impact * 100)}% improvement.
              </Alert>
            </>
          )}
          
          {actionStatus === 'processing' && (
            <VStack py={8} spacing={4}>
              <Spinner size="xl" color={`${colorScheme}.500`} thickness="4px" />
              <Text>Processing your action...</Text>
            </VStack>
          )}
          
          {actionStatus === 'completed' && (
            <VStack py={8} spacing={4} align="center">
              <Icon as={FiCheckCircle} color="green.500" boxSize={12} />
              <Heading size="md">Action Completed Successfully</Heading>
              <Text textAlign="center">
                The recommended actions have been implemented. You should start seeing results in your analytics soon.
              </Text>
            </VStack>
          )}
          
          {actionStatus === 'failed' && (
            <VStack py={8} spacing={4} align="center">
              <Icon as={FiAlertCircle} color="red.500" boxSize={12} />
              <Heading size="md">Action Failed</Heading>
              <Text textAlign="center">
                There was an issue implementing this recommendation. Please try again later or contact support.
              </Text>
            </VStack>
          )}
        </ModalBody>
        
        <ModalFooter>
          {actionStatus === 'pending' && (
            <Button 
              colorScheme={colorScheme} 
              onClick={handleAction}
              rightIcon={<FiArrowRight />}
            >
              Implement Recommendation
            </Button>
          )}
          
          {actionStatus === 'processing' && (
            <Button isDisabled>
              Processing...
            </Button>
          )}
          
          {(actionStatus === 'completed' || actionStatus === 'failed') && (
            <Button onClick={onClose}>
              Close
            </Button>
          )}
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

/**
 * Recommendations Dashboard Component
 * 
 * Main component for displaying and managing recommendations.
 */
export const RecommendationsDashboard = () => {
  const [activeTab, setActiveTab] = useState('all');
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const actionModal = useDisclosure();
  
  // Fetch recommendations
  const { loading, error, data, refetch } = useQuery(GET_RECOMMENDATIONS, {
    variables: { type: null }, // Fetch all types initially
  });
  
  // Handle recommendation action
  const handleAction = (recommendation) => {
    setSelectedRecommendation(recommendation);
    actionModal.onOpen();
  };
  
  // Handle action completion
  const handleActionComplete = () => {
    // Refetch recommendations after action is completed
    setTimeout(() => {
      refetch();
    }, 1000);
  };
  
  // Filter recommendations by type
  const filterRecommendations = (recommendations, type) => {
    if (!recommendations) return [];
    if (type === 'all') return recommendations;
    return recommendations.filter(rec => rec.type === type);
  };
  
  // Get recommendations for current tab
  const currentRecommendations = filterRecommendations(
    data?.recommendations,
    activeTab
  );
  
  // Handle tab change
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    
    // Refetch with type filter if not 'all'
    refetch({
      type: tab === 'all' ? null : tab
    });
  };
  
  // Loading state
  if (loading) {
    return (
      <Flex justify="center" align="center" height="50vh">
        <Spinner size="xl" color="blue.500" thickness="4px" />
      </Flex>
    );
  }
  
  // Error state
  if (error) {
    return (
      <Alert status="error" variant="solid" borderRadius="md">
        <AlertIcon />
        An error occurred while loading recommendations. Please try again later.
      </Alert>
    );
  }
  
  return (
    <Box>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={6}>
        <Box>
          <Heading size="lg">Recommendations</Heading>
          <Text color="gray.500">AI-powered insights to optimize your business</Text>
        </Box>
        <HStack>
          <Button leftIcon={<FiFilter />} variant="outline">
            Filter
          </Button>
          <Button leftIcon={<FiRefreshCw />} colorScheme="blue" onClick={() => refetch()}>
            Refresh
          </Button>
        </HStack>
      </Flex>
      
      {/* Recommendation Stats */}
      <Grid templateColumns={{ base: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }} gap={6} mb={8}>
        <Card>
          <CardBody>
            <VStack align="flex-start">
              <Text color="gray.500">Total Recommendations</Text>
              <Heading size="xl">{data?.recommendations?.length || 0}</Heading>
              <HStack>
                <Badge colorScheme="red">
                  {data?.recommendations?.filter(r => r.impact >= 0.7).length || 0} High Impact
                </Badge>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody>
            <VStack align="flex-start">
              <Text color="gray.500">Inventory Optimizations</Text>
              <Heading size="xl">
                {data?.recommendations?.filter(r => r.type === 'INVENTORY_OPTIMIZATION').length || 0}
              </Heading>
              <Text fontSize="sm" color="blue.500">
                <Icon as={FiPackage} mr={1} />
                Stock management
              </Text>
            </VStack>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody>
            <VStack align="flex-start">
              <Text color="gray.500">Customer Insights</Text>
              <Heading size="xl">
                {data?.recommendations?.filter(r => r.type === 'CUSTOMER_TARGETING').length || 0}
              </Heading>
              <Text fontSize="sm" color="purple.500">
                <Icon as={FiUsers} mr={1} />
                Customer targeting
              </Text>
            </VStack>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody>
            <VStack align="flex-start">
              <Text color="gray.500">Sales Strategies</Text>
              <Heading size="xl">
                {(data?.recommendations?.filter(r => 
                  r.type === 'PRICING_STRATEGY' || 
                  r.type === 'MARKETING_CAMPAIGN' ||
                  r.type === 'PRODUCT_BUNDLING'
                ).length) || 0}
              </Heading>
              <Text fontSize="sm" color="green.500">
                <Icon as={FiTrendingUp} mr={1} />
                Revenue growth
              </Text>
            </VStack>
          </CardBody>
        </Card>
      </Grid>
      
      {/* Recommendation Tabs */}
      <Tabs variant="enclosed" colorScheme="blue" mb={6} onChange={(index) => {
        const tabValues = ['all', 'INVENTORY_OPTIMIZATION', 'CUSTOMER_TARGETING', 'PRICING_STRATEGY', 'MARKETING_CAMPAIGN', 'PRODUCT_BUNDLING'];
        handleTabChange(tabValues[index]);
      }}>
        <TabList>
          <Tab>All</Tab>
          <Tab>Inventory</Tab>
          <Tab>Customers</Tab>
          <Tab>Pricing</Tab>
          <Tab>Marketing</Tab>
          <Tab>Products</Tab>
        </TabList>
      </Tabs>
      
      {/* Recommendations Grid */}
      {currentRecommendations.length > 0 ? (
        <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} gap={6}>
          {currentRecommendations.map((recommendation) => (
            <GridItem key={recommendation.id}>
              <RecommendationCard 
                recommendation={recommendation} 
                onAction={handleAction}
              />
            </GridItem>
          ))}
        </Grid>
      ) : (
        <Box textAlign="center" py={10}>
          <Icon as={FiStar} boxSize={12} color="gray.300" mb={4} />
          <Heading size="md" mb={2}>No Recommendations Available</Heading>
          <Text color="gray.500">
            There are no recommendations for this category at the moment.
          </Text>
        </Box>
      )}
      
      {/* Action Modal */}
      <RecommendationActionModal
        isOpen={actionModal.isOpen}
        onClose={actionModal.onClose}
        recommendation={selectedRecommendation}
        onActionComplete={handleActionComplete}
      />
    </Box>
  );
};

/**
 * Inventory Recommendations Component
 * 
 * Specialized component for inventory recommendations.
 */
export const InventoryRecommendations = () => {
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const actionModal = useDisclosure();
  
  // Fetch inventory recommendations
  const { loading, error, data, refetch } = useQuery(GET_INVENTORY_RECOMMENDATIONS);
  
  // Transform inventory recommendations to standard format
  const transformRecommendations = (invRecs) => {
    if (!invRecs) return [];
    
    return invRecs.map((rec, index) => ({
      id: `inv-rec-${index}`,
      type: 'INVENTORY_OPTIMIZATION',
      title: rec.recommendationType === 'RESTOCK' 
        ? `Restock ${rec.productName}`
        : `Reduce inventory for ${rec.productName}`,
      description: rec.recommendationText,
      impact: rec.recommendationType === 'RESTOCK' ? 0.8 : 0.6,
      confidence: 0.9,
      suggestedActions: [
        rec.recommendationType === 'RESTOCK'
          ? `Order ${rec.recommendedActionValue} units of ${rec.productName}`
          : `Consider promotions to reduce inventory by ${rec.recommendedActionValue} units`
      ],
      relatedEntityId: rec.productId,
      relatedEntityType: 'PRODUCT',
      // Additional inventory-specific data
      currentStock: rec.currentStock,
      reorderPoint: rec.reorderPoint,
      daysOfSupply: rec.daysOfSupply,
      recommendationType: rec.recommendationType,
      recommendedActionValue: rec.recommendedActionValue
    }));
  };
  
  // Get transformed recommendations
  const recommendations = transformRecommendations(data?.inventoryRecommendations);
  
  // Split recommendations by type
  const restockRecommendations = recommendations.filter(rec => rec.recommendationType === 'RESTOCK');
  const reduceRecommendations = recommendations.filter(rec => rec.recommendationType === 'REDUCE_INVENTORY');
  
  // Handle recommendation action
  const handleAction = (recommendation) => {
    setSelectedRecommendation(recommendation);
    actionModal.onOpen();
  };
  
  // Handle action completion
  const handleActionComplete = () => {
    // Refetch recommendations after action is completed
    setTimeout(() => {
      refetch();
    }, 1000);
  };
  
  // Loading state
  if (loading) {
    return (
      <Flex justify="center" align="center" height="50vh">
        <Spinner size="xl" color="blue.500" thickness="4px" />
      </Flex>
    );
  }
  
  // Error state
  if (error) {
    return (
      <Alert status="error" variant="solid" borderRadius="md">
        <AlertIcon />
        An error occurred while loading inventory recommendations. Please try again later.
      </Alert>
    );
  }
  
  return (
    <Box>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={6}>
        <Box>
          <Heading size="lg">Inventory Recommendations</Heading>
          <Text color="gray.500">Optimize your inventory levels and reduce costs</Text>
        </Box>
        <Button leftIcon={<FiRefreshCw />} colorScheme="blue" onClick={() => refetch()}>
          Refresh
        </Button>
      </Flex>
      
      {/* Recommendation Stats */}
      <Grid templateColumns={{ base: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }} gap={6} mb={8}>
        <Card>
          <CardBody>
            <VStack align="flex-start">
              <Text color="gray.500">Total Recommendations</Text>
              <Heading size="xl">{recommendations.length}</Heading>
            </VStack>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody>
            <VStack align="flex-start">
              <Text color="gray.500">Restock Alerts</Text>
              <Heading size="xl">{restockRecommendations.length}</Heading>
              <Badge colorScheme="red">Low Stock</Badge>
            </VStack>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody>
            <VStack align="flex-start">
              <Text color="gray.500">Overstock Alerts</Text>
              <Heading size="xl">{reduceRecommendations.length}</Heading>
              <Badge colorScheme="orange">Excess Inventory</Badge>
            </VStack>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody>
            <VStack align="flex-start">
              <Text color="gray.500">Potential Savings</Text>
              <Heading size="xl">
                {reduceRecommendations.reduce((sum, rec) => sum + rec.recommendedActionValue, 0).toLocaleString()}
              </Heading>
              <Text fontSize="sm" color="green.500">Units of inventory</Text>
            </VStack>
          </CardBody>
        </Card>
      </Grid>
      
      {/* Restock Recommendations */}
      {restockRecommendations.length > 0 && (
        <Box mb={8}>
          <Heading size="md" mb={4}>
            <HStack>
              <Badge colorScheme="red" fontSize="0.8em">URGENT</Badge>
              <Text>Restock Recommendations</Text>
            </HStack>
          </Heading>
          
          <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} gap={6}>
            {restockRecommendations.map((recommendation) => (
              <GridItem key={recommendation.id}>
                <RecommendationCard 
                  recommendation={recommendation} 
                  onAction={handleAction}
                />
              </GridItem>
            ))}
          </Grid>
        </Box>
      )}
      
      {/* Reduce Inventory Recommendations */}
      {reduceRecommendations.length > 0 && (
        <Box>
          <Heading size="md" mb={4}>
            <HStack>
              <Badge colorScheme="orange" fontSize="0.8em">OPTIMIZE</Badge>
              <Text>Reduce Inventory Recommendations</Text>
            </HStack>
          </Heading>
          
          <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} gap={6}>
            {reduceRecommendations.map((recommendation) => (
              <GridItem key={recommendation.id}>
                <RecommendationCard 
                  recommendation={recommendation} 
                  onAction={handleAction}
                />
              </GridItem>
            ))}
          </Grid>
        </Box>
      )}
      
      {/* No Recommendations State */}
      {recommendations.length === 0 && (
        <Box textAlign="center" py={10}>
          <Icon as={FiCheckCircle} boxSize={12} color="green.300" mb={4} />
          <Heading size="md" mb={2}>Inventory Levels Optimal</Heading>
          <Text color="gray.500">
            There are no inventory recommendations at this time. Your inventory levels appear to be optimal.
          </Text>
        </Box>
      )}
      
      {/* Action Modal */}
      <RecommendationActionModal
        isOpen={actionModal.isOpen}
        onClose={actionModal.onClose}
        recommendation={selectedRecommendation}
        onActionComplete={handleActionComplete}
      />
    </Box>
  );
};
