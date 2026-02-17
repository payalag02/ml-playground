require("dotenv").config();

module.exports = {
  port: process.env.PORT || 3000,
  redis: {
    host: process.env.REDIS_HOST || "127.0.0.1",
    port: parseInt(process.env.REDIS_PORT) || 6379,
  },
  cache: {
    defaultTTL: 60, // seconds
  },
  rateLimit: {
    windowMs: 60, // 1 minute window
    maxRequests: 20, // max requests per window
  },
};
