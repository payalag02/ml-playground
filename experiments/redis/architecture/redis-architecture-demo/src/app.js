const express = require("express");
const path = require("path");
const config = require("./config/env");
const rateLimiter = require("./cache-layer/rateLimiter.service");
const userRoutes = require("./api/routes/user.routes");
const metricsRoutes = require("./api/routes/metrics.routes");

// Boot the background worker so it starts processing jobs
require("./workers/queue.worker");

const app = express();

// ── Middleware ──
app.use(express.json());
app.use(rateLimiter); // Redis-backed sliding-window rate limiter

// ── Routes ──
app.use("/api/users", userRoutes);
app.use("/api/metrics", metricsRoutes);

app.get("/health", (_req, res) => res.json({ status: "ok" }));

// Serve the HTML test page
app.use(express.static(path.join(__dirname, "public")));

// ── Start ──
app.listen(config.port, () => {
  console.log(`Server running on http://localhost:${config.port}`);
  console.log("Redis architecture demo ready:");
  console.log("  Cache-aside     → GET /api/users");
  console.log("  Rate limiter    → all routes (20 req/min)");
  console.log("  Real-time count → GET /api/metrics/realtime");
  console.log("  Job queue       → POST /api/metrics/track");
});
