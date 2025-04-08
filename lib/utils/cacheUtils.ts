/**
 * Redis-enabled API cache utility
 * 
 * Provides caching for expensive API calls with configurable TTL
 * and automatic serialization/deserialization.
 */
import Redis from 'ioredis';
import { v4 as uuidv4 } from 'uuid';

// Configure Redis connection - support for both local and cloud Redis
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const REDIS_PASSWORD = process.env.REDIS_PASSWORD;

// Default TTL values for different cache types (in seconds)
const DEFAULT_TTL = {
  PROHANDEL_DATA: 5 * 60, // 5 minutes for inventory, sales data
  MCP_RESPONSES: 30 * 60,  // 30 minutes for AI-generated insights
  AI_CONTEXT: 10 * 60,     // 10 minutes for AI context data
};

// Initialize Redis client with connection retry logic
let redisClient: Redis | null = null;

const getRedisClient = (): Redis | null => {
  if (!redisClient) {
    try {
      redisClient = new Redis(REDIS_URL, {
        password: REDIS_PASSWORD,
        retryStrategy: (times) => {
          // Exponential backoff up to 30 seconds
          const delay = Math.min(times * 100, 30000);
          return delay;
        },
        maxRetriesPerRequest: 3,
      });
      
      redisClient.on('error', (err) => {
        console.error('Redis connection error:', err);
        if (process.env.NODE_ENV === 'production') {
          // Log to monitoring service in production
          console.error('[MONITORING] Redis connection failure - check cloud configuration');
        }
      });
      
      console.log('Redis client initialized');
    } catch (error) {
      console.error('Failed to initialize Redis client:', error);
      // Fall back to in-memory cache if Redis is unavailable
      redisClient = null;
    }
  }
  
  return redisClient;
};

// In-memory fallback cache when Redis is unavailable
const memoryCache: Record<string, { value: any; expires: number }> = {};

/**
 * Gets a value from cache (Redis or in-memory fallback)
 * @param key Cache key
 * @returns Cached value or null if not found/expired
 */
export const getCachedValue = async <T>(key: string): Promise<T | null> => {
  const redis = getRedisClient();
  const fullKey = `mercurios:${key}`;
  
  try {
    if (redis) {
      // Try Redis first
      const cachedData = await redis.get(fullKey);
      if (cachedData) {
        return JSON.parse(cachedData);
      }
    } else if (redis === null) {
      // Fall back to in-memory cache
      const now = Date.now();
      const cacheItem = memoryCache[fullKey];
      
      if (cacheItem && cacheItem.expires > now) {
        return cacheItem.value;
      }
    }
  } catch (error) {
    console.error(`Cache get error for key ${fullKey}:`, error);
  }
  
  return null;
};

/**
 * Stores a value in cache (Redis or in-memory fallback)
 * @param key Cache key
 * @param value Value to cache
 * @param ttlSeconds Time-to-live in seconds
 */
export const setCachedValue = async <T>(
  key: string, 
  value: T, 
  ttlSeconds: number = DEFAULT_TTL.PROHANDEL_DATA
): Promise<void> => {
  const redis = getRedisClient();
  const fullKey = `mercurios:${key}`;
  
  try {
    if (redis) {
      // Store in Redis with TTL
      await redis.set(
        fullKey,
        JSON.stringify(value),
        'EX',
        ttlSeconds
      );
    } else {
      // Fall back to in-memory cache
      memoryCache[fullKey] = {
        value,
        expires: Date.now() + (ttlSeconds * 1000)
      };
    }
  } catch (error) {
    console.error(`Cache set error for key ${fullKey}:`, error);
  }
};

/**
 * Invalidates a cache entry or pattern
 * @param keyPattern Cache key or pattern (with *)
 */
export const invalidateCache = async (keyPattern: string): Promise<void> => {
  const redis = getRedisClient();
  const fullPattern = `mercurios:${keyPattern}`;
  
  try {
    if (redis) {
      // For exact key match
      if (!keyPattern.includes('*')) {
        await redis.del(fullPattern);
      } else {
        // For pattern matching (e.g., 'prohandel:sales:*')
        const keys = await redis.keys(fullPattern);
        if (keys.length) {
          await redis.del(...keys);
        }
      }
    } else {
      // For in-memory cache
      Object.keys(memoryCache).forEach(key => {
        if (key === fullPattern || 
            (keyPattern.includes('*') && 
             key.startsWith(fullPattern.replace('*', '')))) {
          delete memoryCache[key];
        }
      });
    }
  } catch (error) {
    console.error(`Cache invalidation error for pattern ${fullPattern}:`, error);
  }
};

/**
 * Fetches data with caching support - the heart of our caching strategy
 * 
 * @param fetchFn Function that returns a Promise with the data to fetch
 * @param cacheKey Key to use for caching
 * @param ttlSeconds Cache TTL in seconds
 * @param forceFresh Whether to ignore cache and fetch fresh data
 * @returns The fetched or cached data
 */
export const fetchWithCache = async <T>(
  fetchFn: () => Promise<T>,
  cacheKey: string,
  ttlSeconds: number = DEFAULT_TTL.PROHANDEL_DATA,
  forceFresh: boolean = false
): Promise<T> => {
  // Generate a deterministic request ID for tracing
  const requestId = uuidv4().substring(0, 8);
  console.log(`[${requestId}] Cache request for: ${cacheKey}`);
  
  try {
    // Check cache first unless forceFresh is specified
    if (!forceFresh) {
      const cachedData = await getCachedValue<T>(cacheKey);
      if (cachedData) {
        console.log(`[${requestId}] Cache HIT for: ${cacheKey}`);
        return cachedData;
      }
      console.log(`[${requestId}] Cache MISS for: ${cacheKey}`);
    } else {
      console.log(`[${requestId}] Cache BYPASS for: ${cacheKey}`);
    }
    
    // Fetch fresh data
    const startTime = Date.now();
    const freshData = await fetchFn();
    const fetchTime = Date.now() - startTime;
    
    console.log(`[${requestId}] Fetched fresh data in ${fetchTime}ms for: ${cacheKey}`);
    
    // Cache the fresh data
    await setCachedValue(cacheKey, freshData, ttlSeconds);
    
    return freshData;
  } catch (error) {
    console.error(`[${requestId}] Error in fetchWithCache for ${cacheKey}:`, error);
    throw error;
  }
};

/**
 * Specialized cache helper for ProHandel data
 */
export const fetchProHandelDataWithCache = async <T>(
  fetchFn: () => Promise<T>,
  cacheKey: string,
  forceFresh: boolean = false
): Promise<T> => {
  return fetchWithCache(
    fetchFn,
    `prohandel:${cacheKey}`,
    DEFAULT_TTL.PROHANDEL_DATA,
    forceFresh
  );
};

/**
 * Specialized cache helper for MCP responses
 */
export const fetchMcpResponseWithCache = async <T>(
  fetchFn: () => Promise<T>,
  cacheKey: string,
  ttlSeconds: number = DEFAULT_TTL.MCP_RESPONSES
): Promise<T> => {
  return fetchWithCache(
    fetchFn,
    `mcp:${cacheKey}`,
    ttlSeconds
  );
};

/**
 * Creates a hash from an object for use in cache keys
 */
export const hashForCacheKey = (obj: any): string => {
  // Simple but effective for cache key generation
  return Buffer.from(JSON.stringify(obj)).toString('base64')
    .replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
};

// Export default TTL values for convenience
export { DEFAULT_TTL };
