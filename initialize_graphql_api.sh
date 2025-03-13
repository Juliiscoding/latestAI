#!/bin/bash
# Script to initialize a GraphQL API project for Mercurios.ai

echo "Initializing GraphQL API project for Mercurios.ai..."

# Create project directory
mkdir -p ~/mercurios_api
cd ~/mercurios_api

# Initialize npm project
echo "Creating package.json..."
cat > package.json << EOF
{
  "name": "mercurios-api",
  "version": "1.0.0",
  "description": "GraphQL API for Mercurios.ai",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest"
  },
  "author": "Mercurios.ai",
  "license": "ISC",
  "dependencies": {
    "apollo-server": "^3.10.0",
    "graphql": "^16.5.0",
    "snowflake-sdk": "^1.6.0",
    "redis": "^4.2.0",
    "jsonwebtoken": "^8.5.1",
    "dotenv": "^16.0.1"
  },
  "devDependencies": {
    "nodemon": "^2.0.19",
    "jest": "^28.1.3"
  }
}
EOF

# Create .env file
echo "Creating .env file..."
cat > .env << EOF
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=VRXDFZX-ZZ95717
SNOWFLAKE_USERNAME=JULIUSRECHENBACH
SNOWFLAKE_PASSWORD=
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=MERCURIOS_DATA
SNOWFLAKE_ROLE=MERCURIOS_FIVETRAN_SERVICE

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT Configuration
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=1h
REFRESH_TOKEN_EXPIRES_IN=7d

# Server Configuration
PORT=4000
NODE_ENV=development
EOF

# Create project structure
mkdir -p src/schema/resolvers
mkdir -p src/schema/directives
mkdir -p src/datasources
mkdir -p src/utils
mkdir -p src/config

# Create index.js
echo "Creating src/index.js..."
cat > src/index.js << EOF
const { ApolloServer } = require('apollo-server');
const { typeDefs } = require('./schema/typeDefs');
const { resolvers } = require('./schema/resolvers');
const { SnowflakeAPI } = require('./datasources/snowflake');
const { RedisCache } = require('./datasources/redis');
const { getUserFromToken } = require('./utils/auth');
require('dotenv').config();

// Create the Apollo Server
const server = new ApolloServer({
  typeDefs,
  resolvers,
  dataSources: () => ({
    snowflake: new SnowflakeAPI(),
    redis: new RedisCache()
  }),
  context: ({ req }) => {
    // Get the user token from the headers
    const token = req.headers.authorization || '';
    
    // Try to retrieve a user with the token
    const user = getUserFromToken(token);
    
    // Get tenant ID from headers or use default tenant
    const tenantId = req.headers['x-tenant-id'] || (user && user.tenants && user.tenants[0]);
    
    // Add the user and tenant to the context
    return { user, tenantId };
  }
});

// Start the server
const port = process.env.PORT || 4000;
server.listen({ port }).then(({ url }) => {
  console.log(\`🚀 Server ready at \${url}\`);
});
EOF

# Create typeDefs.js
echo "Creating src/schema/typeDefs.js..."
cat > src/schema/typeDefs.js << EOF
const { gql } = require('apollo-server');

const typeDefs = gql\`
  directive @auth(requires: Role = USER) on OBJECT | FIELD_DEFINITION
  
  enum Role {
    USER
    ADMIN
  }

  type Query {
    # Inventory Queries
    inventoryStatus(productId: ID): [InventoryStatus!]!
    reorderRecommendations: [ReorderRecommendation!]!
    
    # Sales Queries
    salesPerformance(period: String!, comparison: String): SalesPerformance!
    productPerformance(period: String!, limit: Int): [ProductPerformance!]!
    
    # Customer Queries
    customerSegments: [CustomerSegment!]!
    customerLifetimeValue(segmentId: ID): [CustomerLTV!]!
  }

  type Mutation {
    # User Management
    login(email: String!, password: String!): AuthPayload!
    refreshToken(token: String!): AuthPayload!
    
    # Tenant Management
    setCurrentTenant(tenantId: ID!): Boolean!
  }

  # Authentication Types
  type AuthPayload {
    token: String!
    refreshToken: String!
    user: User!
  }

  type User {
    id: ID!
    email: String!
    name: String
    role: Role!
    tenants: [Tenant!]!
  }

  type Tenant {
    id: ID!
    name: String!
    domain: String
  }

  # Inventory Types
  type InventoryStatus @auth {
    productId: ID!
    productName: String!
    currentStock: Int!
    reorderPoint: Int!
    avgDailySales: Float
    stockStatus: String!
    daysOfInventory: Int
  }

  type ReorderRecommendation @auth {
    productId: ID!
    productName: String!
    currentStock: Int!
    recommendedOrderQuantity: Int!
    priority: String!
  }

  # Sales Types
  type SalesPerformance @auth {
    period: String!
    totalSales: Float!
    orderCount: Int!
    averageOrderValue: Float!
    comparisonSales: Float
    comparisonOrderCount: Int
    comparisonAverageOrderValue: Float
    salesGrowth: Float
  }

  type ProductPerformance @auth {
    productId: ID!
    productName: String!
    salesQuantity: Int!
    salesValue: Float!
    profitMargin: Float!
    rank: Int!
  }

  # Customer Types
  type CustomerSegment @auth {
    segmentId: ID!
    segmentName: String!
    customerCount: Int!
    averageLTV: Float!
    averageOrderFrequency: Float!
  }

  type CustomerLTV @auth {
    customerId: ID!
    customerName: String!
    lifetimeValue: Float!
    orderCount: Int!
    firstOrderDate: String!
    lastOrderDate: String!
    segmentId: ID
    segmentName: String
  }
\`;

module.exports = { typeDefs };
EOF

# Create resolvers.js
echo "Creating src/schema/resolvers/index.js..."
cat > src/schema/resolvers/index.js << EOF
const inventoryResolvers = require('./inventory');
const salesResolvers = require('./sales');
const customerResolvers = require('./customers');
const authResolvers = require('./auth');

// Merge resolvers
const resolvers = {
  Query: {
    ...inventoryResolvers.Query,
    ...salesResolvers.Query,
    ...customerResolvers.Query
  },
  Mutation: {
    ...authResolvers.Mutation
  }
};

module.exports = { resolvers };
EOF

# Create inventory resolvers
echo "Creating src/schema/resolvers/inventory.js..."
cat > src/schema/resolvers/inventory.js << EOF
const Query = {
  inventoryStatus: async (_, { productId }, { dataSources, tenantId }) => {
    // Set tenant context in Snowflake
    await dataSources.snowflake.setTenantContext(tenantId);
    
    // Build query based on whether a productId was provided
    let query = \`
      SELECT 
        product_id as "productId",
        product_name as "productName",
        current_stock as "currentStock",
        reorder_point as "reorderPoint",
        avg_daily_sales as "avgDailySales",
        stock_status as "stockStatus",
        days_of_inventory as "daysOfInventory"
      FROM 
        MERCURIOS_DATA.ANALYTICS.INVENTORY_STATUS
    \`;
    
    if (productId) {
      query += \` WHERE product_id = '\${productId}'\`;
    }
    
    // Execute query and return results
    return dataSources.snowflake.query(query);
  },
  
  reorderRecommendations: async (_, __, { dataSources, tenantId }) => {
    await dataSources.snowflake.setTenantContext(tenantId);
    
    const query = \`
      SELECT 
        product_id as "productId",
        product_name as "productName",
        current_stock as "currentStock",
        recommended_order_quantity as "recommendedOrderQuantity",
        priority
      FROM 
        MERCURIOS_DATA.ANALYTICS.REORDER_RECOMMENDATIONS
      ORDER BY 
        CASE 
          WHEN priority = 'High' THEN 1
          WHEN priority = 'Medium' THEN 2
          WHEN priority = 'Low' THEN 3
          ELSE 4
        END
    \`;
    
    return dataSources.snowflake.query(query);
  }
};

module.exports = { Query };
EOF

# Create snowflake.js
echo "Creating src/datasources/snowflake.js..."
cat > src/datasources/snowflake.js << EOF
const { DataSource } = require('apollo-datasource');
const snowflake = require('snowflake-sdk');

class SnowflakeAPI extends DataSource {
  constructor() {
    super();
    this.connection = snowflake.createConnection({
      account: process.env.SNOWFLAKE_ACCOUNT,
      username: process.env.SNOWFLAKE_USERNAME,
      password: process.env.SNOWFLAKE_PASSWORD,
      warehouse: process.env.SNOWFLAKE_WAREHOUSE,
      database: process.env.SNOWFLAKE_DATABASE,
      role: process.env.SNOWFLAKE_ROLE
    });
    
    this.connection.connect((err) => {
      if (err) {
        console.error('Unable to connect to Snowflake:', err);
      } else {
        console.log('Successfully connected to Snowflake');
      }
    });
  }
  
  async query(sqlText) {
    return new Promise((resolve, reject) => {
      this.connection.execute({
        sqlText,
        complete: (err, stmt, rows) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows);
          }
        }
      });
    });
  }
  
  async setTenantContext(tenantId) {
    if (!tenantId) return;
    
    return this.query(\`CALL MERCURIOS_DATA.PUBLIC.SET_TENANT_CONTEXT('\${tenantId}')\`);
  }
}

module.exports = { SnowflakeAPI };
EOF

# Create redis.js
echo "Creating src/datasources/redis.js..."
cat > src/datasources/redis.js << EOF
const { DataSource } = require('apollo-datasource');
const Redis = require('redis');

class RedisCache extends DataSource {
  constructor() {
    super();
    this.client = Redis.createClient({
      url: \`redis://\${process.env.REDIS_HOST}:\${process.env.REDIS_PORT}\`,
      password: process.env.REDIS_PASSWORD
    });
    
    this.client.on('error', (err) => {
      console.error('Redis error:', err);
    });
    
    this.client.connect().catch(console.error);
  }
  
  async get(key) {
    const value = await this.client.get(key);
    return value ? JSON.parse(value) : null;
  }
  
  async set(key, value, ttl = 3600) {
    await this.client.set(key, JSON.stringify(value), { EX: ttl });
    return value;
  }
  
  async invalidate(key) {
    await this.client.del(key);
  }
  
  async invalidatePattern(pattern) {
    const keys = await this.client.keys(pattern);
    if (keys.length > 0) {
      await this.client.del(keys);
    }
  }
}

module.exports = { RedisCache };
EOF

# Create auth.js
echo "Creating src/utils/auth.js..."
cat > src/utils/auth.js << EOF
const jwt = require('jsonwebtoken');
const { AuthenticationError } = require('apollo-server');

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '1h';
const REFRESH_TOKEN_EXPIRES_IN = process.env.REFRESH_TOKEN_EXPIRES_IN || '7d';

const generateTokens = (user) => {
  const token = jwt.sign(
    { 
      id: user.id, 
      email: user.email, 
      role: user.role,
      tenants: user.tenants.map(t => t.id)
    },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );
  
  const refreshToken = jwt.sign(
    { id: user.id },
    JWT_SECRET,
    { expiresIn: REFRESH_TOKEN_EXPIRES_IN }
  );
  
  return { token, refreshToken };
};

const verifyToken = (token) => {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    throw new AuthenticationError('Invalid or expired token');
  }
};

const getUserFromToken = (token) => {
  if (!token) return null;
  
  try {
    // Remove "Bearer " prefix if present
    const tokenString = token.startsWith('Bearer ') ? token.slice(7) : token;
    return verifyToken(tokenString);
  } catch (error) {
    return null;
  }
};

module.exports = { generateTokens, verifyToken, getUserFromToken };
EOF

# Create README.md
echo "Creating README.md..."
cat > README.md << EOF
# Mercurios.ai GraphQL API

This is the GraphQL API for Mercurios.ai, providing access to retail analytics and inventory management data.

## Getting Started

1. Install dependencies:
\`\`\`
npm install
\`\`\`

2. Set up environment variables:
\`\`\`
cp .env.example .env
\`\`\`
Then edit the .env file with your credentials.

3. Start the development server:
\`\`\`
npm run dev
\`\`\`

4. Open GraphQL Playground at http://localhost:4000

## Available Queries

- \`inventoryStatus\`: Get current inventory status
- \`reorderRecommendations\`: Get recommendations for reordering products
- \`salesPerformance\`: Get sales performance metrics
- \`productPerformance\`: Get product performance metrics
- \`customerSegments\`: Get customer segment information
- \`customerLifetimeValue\`: Get customer lifetime value metrics

## Authentication

This API uses JWT for authentication. To authenticate:

1. Call the \`login\` mutation with valid credentials
2. Use the returned token in the Authorization header:
\`\`\`
Authorization: Bearer <token>
\`\`\`

## Multi-Tenant Support

To specify a tenant, include the \`x-tenant-id\` header in your requests:
\`\`\`
x-tenant-id: <tenant_id>
\`\`\`
EOF

echo "GraphQL API project initialized at ~/mercurios_api"
echo "To install dependencies, run: cd ~/mercurios_api && npm install"
echo "To start the development server, run: cd ~/mercurios_api && npm run dev"
