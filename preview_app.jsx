/**
 * Earth Module Preview Application
 * 
 * This is a simple Next.js application to preview the Earth module components.
 */

import React from 'react';
import { ChakraProvider, Box, Heading, Text, Button } from '@chakra-ui/react';
import { ApolloProvider, ApolloClient, InMemoryCache } from '@apollo/client';
import { EarthDashboard } from './earth_dashboard_main';
import { RecommendationsDashboard } from './earth_recommendation_engine';

// Create Apollo Client
const client = new ApolloClient({
  uri: 'http://localhost:3000/api/graphql',
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'no-cache',
      errorPolicy: 'all',
    },
    query: {
      fetchPolicy: 'no-cache',
      errorPolicy: 'all',
    },
  },
});

// Main Preview Component
export default function PreviewApp() {
  return (
    <ChakraProvider>
      <ApolloProvider client={client}>
        <Box p={4}>
          <Heading mb={6}>Earth Module Preview</Heading>
          <Text mb={8}>This is a preview of the Earth module components with mock data.</Text>
          
          <Box mb={10}>
            <Heading size="md" mb={4}>Dashboard Preview</Heading>
            <Box border="1px solid" borderColor="gray.200" borderRadius="md" overflow="hidden">
              <EarthDashboard />
            </Box>
          </Box>
          
          <Box mb={10}>
            <Heading size="md" mb={4}>Recommendations Dashboard Preview</Heading>
            <Box border="1px solid" borderColor="gray.200" borderRadius="md" overflow="hidden" p={6}>
              <RecommendationsDashboard />
            </Box>
          </Box>
        </Box>
      </ApolloProvider>
    </ChakraProvider>
  );
}
