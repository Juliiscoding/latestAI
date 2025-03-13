/**
 * Earth Module GraphQL API Endpoint
 * 
 * This file implements the API endpoint for the Earth module GraphQL API.
 * It can be placed in the /pages/api/earth/graphql.js file of your Next.js application.
 */

import { ApolloServer } from 'apollo-server-micro';
import { getSession } from 'next-auth/react';
import typeDefs from '../../../lib/earth/graphql/schema';
import resolvers from '../../../lib/earth/graphql/resolvers';
import { getTenantIdFromSession } from '../../../lib/auth/tenant';

// Configure Apollo Server
const apolloServer = new ApolloServer({
  typeDefs,
  resolvers,
  context: async ({ req }) => {
    // Get session from NextAuth
    const session = await getSession({ req });
    
    // Check authentication
    if (!session) {
      throw new Error('You must be authenticated to access this API');
    }
    
    // Get tenant ID from session
    const tenantId = getTenantIdFromSession(session);
    
    // Return context with tenant ID
    return {
      tenantId,
      user: session.user
    };
  },
  formatError: (error) => {
    // Log server errors but return sanitized errors to client
    console.error('GraphQL Error:', error);
    
    // Don't expose internal server errors to clients
    if (error.extensions?.code === 'INTERNAL_SERVER_ERROR') {
      return {
        message: 'An internal error occurred',
        extensions: {
          code: 'INTERNAL_SERVER_ERROR'
        }
      };
    }
    
    return error;
  }
});

// Start Apollo Server
const startServer = apolloServer.start();

// Configure API endpoint
export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', process.env.NEXT_PUBLIC_FRONTEND_URL || '*');
  res.setHeader('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  
  // Handle OPTIONS request
  if (req.method === 'OPTIONS') {
    res.end();
    return false;
  }
  
  // Start Apollo Server if not already started
  await startServer;
  
  // Create handler
  const handler = apolloServer.createHandler({
    path: '/api/earth/graphql',
  });
  
  // Run handler
  await handler(req, res);
}

// Configure API route
export const config = {
  api: {
    bodyParser: false,
  },
};
