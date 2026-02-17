const Redis = require("ioredis");
const config = require("../config/env");

// Singleton Redis connection
let client = null;

function getRedisClient() {
  if (!client) {
    client = new Redis({
      host: config.redis.host,
      port: config.redis.port,
      maxRetriesPerRequest: 3,
      retryStrategy(times) {
        const delay = Math.min(times * 200, 2000);
        return delay;
      },
    });

    client.on("connect", () => console.log("[Redis] Connected"));
    client.on("error", (err) => console.error("[Redis] Error:", err.message));
  }

  return client;
}

module.exports = { getRedisClient };
