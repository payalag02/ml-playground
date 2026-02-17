const metricsRepo = require("../persistence-layer/metrics.repository");
const cacheService = require("../cache-layer/cache.service");
const { getRedisClient } = require("../cache-layer/redis.client");

const redis = getRedisClient();
const CACHE_PREFIX = "metrics";

const metricsService = {
  /**
   * Fast-track: increment a real-time counter in Redis,
   * then enqueue a persistent write via BullMQ (see queue.worker.js).
   */
  async trackEvent(eventName, payload = {}) {
    // Real-time counter in Redis (instantaneous, no DB hit)
    await redis.hincrby("metrics:realtime", eventName, 1);

    // Also persist to SQLite for historical queries
    await metricsRepo.record(eventName, payload);

    // Invalidate cached aggregates
    await cacheService.del(`${CACHE_PREFIX}:counts`);
  },

  /**
   * Returns real-time counters straight from Redis (sub-ms).
   */
  async getRealtimeCounts() {
    return redis.hgetall("metrics:realtime");
  },

  /**
   * Returns persisted aggregates from the DB (cached).
   */
  async getPersistedCounts() {
    return cacheService.getOrSet(
      `${CACHE_PREFIX}:counts`,
      () => metricsRepo.countByEvent(),
      15
    );
  },

  async getEventHistory(eventName) {
    return metricsRepo.getByEvent(eventName);
  },
};

module.exports = metricsService;
