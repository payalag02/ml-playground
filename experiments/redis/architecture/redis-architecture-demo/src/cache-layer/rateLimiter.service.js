const { getRedisClient } = require("./redis.client");
const config = require("../config/env");

const redis = getRedisClient();

/**
 * Sliding-window rate limiter using Redis sorted sets.
 *
 * How it works:
 *   - Each request adds a timestamped entry to a sorted set keyed by IP.
 *   - Old entries outside the window are pruned.
 *   - If the remaining count exceeds the limit, the request is rejected.
 */
async function rateLimiterMiddleware(req, res, next) {
  const key = `ratelimit:${req.ip}`;
  const now = Date.now();
  const windowStart = now - config.rateLimit.windowMs * 1000;

  const multi = redis.multi();
  // Remove entries older than the window
  multi.zremrangebyscore(key, 0, windowStart);
  // Add current request
  multi.zadd(key, now, `${now}-${Math.random()}`);
  // Count requests in window
  multi.zcard(key);
  // Auto-expire the key after the window passes
  multi.expire(key, config.rateLimit.windowMs);

  const results = await multi.exec();
  const requestCount = results[2][1];

  res.set("X-RateLimit-Limit", config.rateLimit.maxRequests);
  res.set("X-RateLimit-Remaining", Math.max(0, config.rateLimit.maxRequests - requestCount));

  if (requestCount > config.rateLimit.maxRequests) {
    return res.status(429).json({
      error: "Too many requests",
      retryAfterSeconds: config.rateLimit.windowMs,
    });
  }

  next();
}

module.exports = rateLimiterMiddleware;
