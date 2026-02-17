const { getRedisClient } = require("./redis.client");
const config = require("../config/env");

const redis = getRedisClient();

const cacheService = {
  /**
   * Get a cached value. Returns parsed JSON or null.
   */
  async get(key) {
    const data = await redis.get(key);
    if (!data) return null;
    try {
      return JSON.parse(data);
    } catch {
      return data;
    }
  },

  /**
   * Set a value in cache with optional TTL (seconds).
   */
  async set(key, value, ttl = config.cache.defaultTTL) {
    const serialized = JSON.stringify(value);
    if (ttl) {
      await redis.set(key, serialized, "EX", ttl);
    } else {
      await redis.set(key, serialized);
    }
  },

  /**
   * Delete a cached key.
   */
  async del(key) {
    await redis.del(key);
  },

  /**
   * Invalidate all keys matching a pattern (e.g. "user:*").
   */
  async invalidatePattern(pattern) {
    const keys = await redis.keys(pattern);
    if (keys.length > 0) {
      await redis.del(...keys);
    }
    return keys.length;
  },

  /**
   * Cache-aside pattern: return cached value or fetch & cache it.
   */
  async getOrSet(key, fetchFn, ttl = config.cache.defaultTTL) {
    const cached = await this.get(key);
    if (cached !== null) {
      console.log(`[Cache] HIT  ${key}`);
      return cached;
    }
    console.log(`[Cache] MISS ${key}`);
    const freshData = await fetchFn();
    await this.set(key, freshData, ttl);
    return freshData;
  },
};

module.exports = cacheService;
