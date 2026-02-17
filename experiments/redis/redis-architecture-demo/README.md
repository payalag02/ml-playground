# Redis Architecture Demo

A production-style Node.js application demonstrating professional Redis architecture patterns — caching, rate limiting, real-time metrics, and job queues — built with clean layered architecture.

## Architecture

```
┌──────────────────────────────────────────────┐
│            Express API Layer                 │
│         Routes → Controllers                │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│            Domain Services                   │
│     Business logic & orchestration           │
└────────┬─────────────────────────┬───────────┘
         │                         │
┌────────▼─────────┐   ┌──────────▼───────────┐
│   Cache Layer    │   │  Persistence Layer   │
│   (Redis)        │   │  (SQLite via sql.js) │
│ • Caching        │   │  • User Repository   │
│ • Rate Limiting  │   │  • Metrics Repository│
│ • Real-time      │   │                      │
│   Counters       │   │                      │
│ • Job Queues     │   │                      │
└──────────────────┘   └──────────────────────┘
```

## Key Features

### 1. Cache-Aside Pattern
Transparent caching with automatic TTL expiration and invalidation on writes. Cache checks Redis first; on a miss, fetches from the database and populates the cache.

### 2. Sliding-Window Rate Limiter
Per-IP rate limiting using Redis sorted sets. Tracks 20 requests per 60-second sliding window with precise pruning. Returns `429 Too Many Requests` when exceeded, along with `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers.

### 3. Real-Time Metrics
Dual-layer approach — Redis hashes for instant counters (`HINCRBY`) and SQLite for persistent historical data. Reads from Redis are sub-millisecond; writes are persisted asynchronously.

### 4. Job Queue (BullMQ)
Background job processing for metric persistence. The API returns `202 Accepted` immediately while a worker (concurrency: 5) processes database writes in the background.

## Tech Stack

| Layer         | Technology               |
|---------------|--------------------------|
| Server        | Express.js               |
| Cache / Queue | Redis (via ioredis)      |
| Job Queue     | BullMQ                   |
| Database      | SQLite (via sql.js)      |
| Containers    | Docker & Docker Compose  |

## Project Structure

```
src/
├── api/
│   ├── controllers/        # Request handlers
│   │   ├── user.controller.js
│   │   └── metrics.controller.js
│   └── routes/             # Express route definitions
│       ├── user.routes.js
│       └── metrics.routes.js
├── cache-layer/
│   ├── redis.client.js         # Redis singleton with retry logic
│   ├── cache.service.js        # Cache-aside implementation
│   └── rateLimiter.service.js  # Sliding-window rate limiter
├── persistence-layer/
│   ├── db.client.js            # SQLite client (in-memory + file persist)
│   ├── user.repository.js      # User data access
│   └── metrics.repository.js   # Metrics data access
├── domain/
│   ├── user.service.js         # User business logic
│   └── metrics.service.js      # Metrics business logic
├── workers/
│   └── queue.worker.js         # BullMQ background worker
├── config/
│   └── env.js                  # Environment configuration
├── public/
│   └── index.html              # Interactive testing dashboard
└── app.js                      # Entry point
```

## Getting Started

### Prerequisites

- Node.js (v18+)
- Redis server (or Docker)

### Option 1: Docker (recommended)

```bash
docker-compose up
```

This starts both Redis (port 6379) and the app (port 3000).

### Option 2: Local Development

Make sure Redis is running locally, then:

```bash
npm install
npm run dev
```

The server starts on `http://localhost:3000`.

### Environment Variables

| Variable     | Default     | Description          |
|--------------|-------------|----------------------|
| `PORT`       | `3000`      | Server port          |
| `REDIS_HOST` | `127.0.0.1` | Redis host           |
| `REDIS_PORT` | `6379`      | Redis port           |

## API Endpoints

### Users

| Method   | Endpoint         | Description                        |
|----------|------------------|------------------------------------|
| `GET`    | `/api/users`     | List all users (cached, 30s TTL)   |
| `GET`    | `/api/users/:id` | Get user by ID (cached, 60s TTL)   |
| `POST`   | `/api/users`     | Create user + invalidate cache     |
| `PUT`    | `/api/users/:id` | Update user + invalidate cache     |
| `DELETE` | `/api/users/:id` | Delete user + invalidate cache     |

### Metrics

| Method | Endpoint                    | Description                            |
|--------|-----------------------------|----------------------------------------|
| `POST` | `/api/metrics/track`        | Track event (Redis instant + DB async) |
| `GET`  | `/api/metrics/realtime`     | Real-time counters from Redis          |
| `GET`  | `/api/metrics/persisted`    | Persisted aggregates (cached, 15s TTL) |
| `GET`  | `/api/metrics/history/:event` | Historical data for a specific event |

### Health

| Method | Endpoint  | Description              |
|--------|-----------|--------------------------|
| `GET`  | `/health` | Health check (rate limited) |

## Interactive Dashboard

Navigate to `http://localhost:3000` for an interactive UI that lets you:

- Create and list users with cache hit/miss visualization
- Track events and view real-time counters
- Stress-test the rate limiter (fires 25 rapid requests)
- Inspect request/response logs

## Database Schema

```sql
CREATE TABLE users (
  id         TEXT PRIMARY KEY,
  name       TEXT NOT NULL,
  email      TEXT NOT NULL UNIQUE,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE metrics (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  event_name TEXT NOT NULL,
  payload    TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
```

## Implementation Notes

- **Redis connection** uses a singleton with exponential backoff retry (max 3 retries, 2s cap)
- **Cache invalidation** uses both individual key deletion and pattern-based invalidation (`user:*`)
- **SQLite** runs in-memory via sql.js and persists to `data.db` on every write
- **Rate limiter** uses Redis sorted sets with atomic pipeline operations for precision
