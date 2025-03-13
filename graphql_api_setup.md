# GraphQL API Setup for Mercurios.ai

This guide outlines how to set up a GraphQL API for Mercurios.ai that will serve as the data access layer between your Snowflake data warehouse and your Next.js frontend.

## Technology Stack

- **Node.js** with TypeScript
- **Apollo Server** for GraphQL implementation
- **Prisma** for database access
- **Redis** for caching
- **JWT** for authentication
- **Docker** for containerization

## Project Structure

```
mercurios-api/
├── src/
│   ├── index.ts                  # Entry point
│   ├── schema/                   # GraphQL schema
│   │   ├── typeDefs.ts           # Type definitions
│   │   ├── resolvers/            # Resolvers
│   │   │   ├── inventory.ts      # Inventory resolvers
│   │   │   ├── sales.ts          # Sales resolvers
│   │   │   └── customers.ts      # Customer resolvers
│   │   └── directives/           # Custom directives
│   │       └── auth.ts           # Authentication directive
│   ├── datasources/              # Data sources
│   │   ├── snowflake.ts          # Snowflake connector
│   │   └── redis.ts              # Redis connector
│   ├── utils/                    # Utility functions
│   │   ├── auth.ts               # Authentication utilities
│   │   ├── tenant.ts             # Tenant isolation utilities
│   │   └── cache.ts              # Caching utilities
│   └── config/                   # Configuration
│       └── index.ts              # Configuration loader
├── prisma/                       # Prisma ORM
│   └── schema.prisma             # Database schema
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── package.json                  # Dependencies
└── tsconfig.json                 # TypeScript configuration
```

## Implementation Steps

### 1. Initialize the Project

```bash
mkdir mercurios-api
cd mercurios-api
npm init -y
npm install apollo-server graphql prisma @prisma/client redis jsonwebtoken dotenv
npm install --save-dev typescript ts-node @types/node @types/jsonwebtoken
npx tsc --init
```

### 2. Set Up GraphQL Schema

Create a basic schema that defines your data model:

```typescript
// src/schema/typeDefs.ts
import { gql } from 'apollo-server';

export const typeDefs = gql`
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
`;
```

### 3. Implement Resolvers

Create resolvers to handle GraphQL queries:

```typescript
// src/schema/resolvers/inventory.ts
export const inventoryResolvers = {
  Query: {
    inventoryStatus: async (_, { productId }, { dataSources, tenantId }) => {
      // Set tenant context in Snowflake
      await dataSources.snowflake.setTenantContext(tenantId);
      
      // Build query based on whether a productId was provided
      let query = `
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
      `;
      
      if (productId) {
        query += ` WHERE product_id = '${productId}'`;
      }
      
      // Execute query and return results
      return dataSources.snowflake.query(query);
    },
    
    reorderRecommendations: async (_, __, { dataSources, tenantId }) => {
      await dataSources.snowflake.setTenantContext(tenantId);
      
      const query = `
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
      `;
      
      return dataSources.snowflake.query(query);
    }
  }
};
```

### 4. Set Up Snowflake Data Source

Create a data source to connect to Snowflake:

```typescript
// src/datasources/snowflake.ts
import { DataSource } from 'apollo-datasource';
import snowflake from 'snowflake-sdk';

export class SnowflakeAPI extends DataSource {
  private connection;
  
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
    
    return this.query(`CALL MERCURIOS_DATA.PUBLIC.SET_TENANT_CONTEXT('${tenantId}')`);
  }
}
```

### 5. Implement Authentication

Set up JWT authentication:

```typescript
// src/utils/auth.ts
import jwt from 'jsonwebtoken';
import { AuthenticationError } from 'apollo-server';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const JWT_EXPIRES_IN = '1h';
const REFRESH_TOKEN_EXPIRES_IN = '7d';

export const generateTokens = (user) => {
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

export const verifyToken = (token) => {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    throw new AuthenticationError('Invalid or expired token');
  }
};

export const getUserFromToken = (token) => {
  if (!token) return null;
  
  try {
    // Remove "Bearer " prefix if present
    const tokenString = token.startsWith('Bearer ') ? token.slice(7) : token;
    return verifyToken(tokenString);
  } catch (error) {
    return null;
  }
};
```

### 6. Implement Caching with Redis

Set up Redis for caching:

```typescript
// src/datasources/redis.ts
import { DataSource } from 'apollo-datasource';
import Redis from 'ioredis';

export class RedisCache extends DataSource {
  private client;
  
  constructor() {
    super();
    this.client = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD
    });
  }
  
  async get(key) {
    const value = await this.client.get(key);
    return value ? JSON.parse(value) : null;
  }
  
  async set(key, value, ttl = 3600) {
    await this.client.set(key, JSON.stringify(value), 'EX', ttl);
    return value;
  }
  
  async invalidate(key) {
    await this.client.del(key);
  }
  
  async invalidatePattern(pattern) {
    const keys = await this.client.keys(pattern);
    if (keys.length > 0) {
      await this.client.del(...keys);
    }
  }
}
```

### 7. Set Up the Apollo Server

Create the main server file:

```typescript
// src/index.ts
import { ApolloServer } from 'apollo-server';
import { typeDefs } from './schema/typeDefs';
import { inventoryResolvers } from './schema/resolvers/inventory';
import { salesResolvers } from './schema/resolvers/sales';
import { customerResolvers } from './schema/resolvers/customers';
import { SnowflakeAPI } from './datasources/snowflake';
import { RedisCache } from './datasources/redis';
import { getUserFromToken } from './utils/auth';
import { SchemaDirectiveVisitor } from 'apollo-server';
import { AuthDirective } from './schema/directives/auth';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Merge resolvers
const resolvers = {
  Query: {
    ...inventoryResolvers.Query,
    ...salesResolvers.Query,
    ...customerResolvers.Query
  },
  Mutation: {
    // Mutation resolvers would go here
  }
};

// Create the Apollo Server
const server = new ApolloServer({
  typeDefs,
  resolvers,
  schemaDirectives: {
    auth: AuthDirective
  },
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
server.listen({ port: process.env.PORT || 4000 }).then(({ url }) => {
  console.log(`🚀 Server ready at ${url}`);
});
```

### 8. Create a Docker Configuration

Set up Docker for containerization:

```dockerfile
# Dockerfile
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 4000

CMD ["npm", "start"]
```

```yaml
# docker-compose.yml
version: '3'

services:
  api:
    build: .
    ports:
      - "4000:4000"
    environment:
      - NODE_ENV=production
      - PORT=4000
      - SNOWFLAKE_ACCOUNT=${SNOWFLAKE_ACCOUNT}
      - SNOWFLAKE_USERNAME=${SNOWFLAKE_USERNAME}
      - SNOWFLAKE_PASSWORD=${SNOWFLAKE_PASSWORD}
      - SNOWFLAKE_WAREHOUSE=${SNOWFLAKE_WAREHOUSE}
      - SNOWFLAKE_DATABASE=${SNOWFLAKE_DATABASE}
      - SNOWFLAKE_ROLE=${SNOWFLAKE_ROLE}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

## Usage Examples

### Querying Inventory Status

```graphql
query GetInventoryStatus {
  inventoryStatus {
    productId
    productName
    currentStock
    stockStatus
    daysOfInventory
  }
}
```

### Querying Sales Performance

```graphql
query GetSalesPerformance {
  salesPerformance(period: "LAST_30_DAYS", comparison: "PREVIOUS_PERIOD") {
    totalSales
    orderCount
    averageOrderValue
    salesGrowth
  }
}
```

### Authentication

```graphql
mutation Login {
  login(email: "user@example.com", password: "password123") {
    token
    refreshToken
    user {
      id
      name
      email
      role
      tenants {
        id
        name
      }
    }
  }
}
```

## Next Steps

1. **Implement Remaining Resolvers**: Complete the implementation of all resolvers for sales and customer data.
2. **Add Error Handling**: Implement comprehensive error handling throughout the API.
3. **Set Up Monitoring**: Add logging and monitoring to track API performance and errors.
4. **Implement Rate Limiting**: Add rate limiting to protect against abuse.
5. **Add Unit Tests**: Create tests for resolvers, data sources, and authentication.
6. **Set Up CI/CD**: Configure continuous integration and deployment pipelines.
7. **Create API Documentation**: Generate API documentation using GraphQL introspection.

## Security Considerations

1. **Environment Variables**: Store all sensitive information in environment variables.
2. **Input Validation**: Validate all user inputs to prevent SQL injection.
3. **Rate Limiting**: Implement rate limiting to prevent abuse.
4. **Authentication**: Ensure all sensitive endpoints require authentication.
5. **Authorization**: Use the `@auth` directive to enforce role-based access control.
6. **Tenant Isolation**: Ensure data is properly isolated between tenants.
7. **Audit Logging**: Implement audit logging for sensitive operations.
