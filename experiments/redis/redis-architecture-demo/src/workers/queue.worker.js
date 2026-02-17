const { Queue, Worker } = require("bullmq");
const config = require("../config/env");
const metricsRepo = require("../persistence-layer/metrics.repository");

const connection = { host: config.redis.host, port: config.redis.port };

// ── Queue ──
const metricsQueue = new Queue("metrics-persist", { connection });

/**
 * Enqueue a metric event for async persistence.
 * Use this when you want fire-and-forget writes that don't block the API response.
 */
async function enqueueMetric(eventName, payload = {}) {
  await metricsQueue.add("persist", { eventName, payload });
}

// ── Worker ──
const worker = new Worker(
  "metrics-persist",
  async (job) => {
    const { eventName, payload } = job.data;
    await metricsRepo.record(eventName, payload);
    console.log(`[Worker] Persisted metric: ${eventName}`);
  },
  { connection, concurrency: 5 }
);

worker.on("completed", (job) => {
  console.log(`[Worker] Job ${job.id} completed`);
});

worker.on("failed", (job, err) => {
  console.error(`[Worker] Job ${job.id} failed:`, err.message);
});

module.exports = { metricsQueue, enqueueMetric };
