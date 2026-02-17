# Redis Pub/Sub - Production-Ready Implementation

A complete, production-ready implementation of Redis Pub/Sub pattern in Python with robust error handling, connection management, and example message handlers for ML workflows.

## Features

✅ **Production-Ready**
- Connection pooling and automatic reconnection
- Graceful shutdown handling (SIGINT/SIGTERM)
- Comprehensive error handling and logging
- Health checks and keep-alive

✅ **Publisher Features**
- Single and batch message publishing
- Automatic timestamp injection
- JSON serialization
- Subscriber count tracking

✅ **Subscriber Features**
- Custom message handlers per channel
- Multi-channel subscription
- Automatic message parsing
- Signal-based graceful shutdown

## Prerequisites

- Python 3.8+
- Redis server running locally or remotely

## Installation

### 1. Install Redis Server

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**Docker:**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Terminal 1: Start the Subscriber

```bash
python subscriber.py
```

You should see:
```
2024-XX-XX XX:XX:XX - __main__ - INFO - Successfully connected to Redis at localhost:6379
2024-XX-XX XX:XX:XX - __main__ - INFO - Subscribed to channels: ml_events, notifications, audit_log
2024-XX-XX XX:XX:XX - __main__ - INFO - Subscriber is ready and listening for messages...
```

### Terminal 2: Run the Publisher

```bash
python publisher.py
```

The publisher will send example messages and you'll see them appear in the subscriber terminal.

## Usage Examples

### Basic Publisher

```python
from publisher import RedisPublisher

# Initialize
publisher = RedisPublisher(host='localhost', port=6379)

# Publish a message
message = {
    'event': 'model_training_started',
    'model_name': 'random_forest',
    'parameters': {'n_estimators': 100}
}
publisher.publish_message('ml_events', message)

# Clean up
publisher.close()
```

### Batch Publishing

```python
messages = [
    {'event': 'data_processed', 'rows': 1000},
    {'event': 'model_trained', 'accuracy': 0.95},
    {'event': 'deployment_ready', 'version': '1.0'}
]

# Publish with 0.5s delay between messages
success, failed = publisher.publish_batch('ml_events', messages, delay=0.5)
print(f"Published: {success}, Failed: {failed}")
```

### Basic Subscriber

```python
from subscriber import RedisSubscriber

# Initialize
subscriber = RedisSubscriber(host='localhost', port=6379)

# Connect
subscriber.connect()

# Subscribe to channels
subscriber.subscribe('ml_events', 'notifications')

# Start listening (blocks until interrupted)
subscriber.listen()
```

### Custom Message Handlers

```python
from subscriber import RedisSubscriber

def my_handler(data):
    """Custom handler for processing messages"""
    print(f"Received: {data}")
    # Your custom logic here
    if data.get('event') == 'critical_alert':
        send_email_notification(data)

# Register handler for specific channel
subscriber = RedisSubscriber()
subscriber.connect()
subscriber.register_handler('alerts', my_handler)
subscriber.subscribe('alerts')
subscriber.listen()
```

## Architecture

```
┌─────────────┐                    ┌─────────────┐
│  Publisher  │                    │  Publisher  │
│   (App 1)   │                    │   (App 2)   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │          PUBLISH                 │
       └─────────────┐   ┌────────────────┘
                     ▼   ▼
              ┌─────────────────┐
              │   Redis Server  │
              │   (Pub/Sub)     │
              └─────────────────┘
                     │   │
       ┌─────────────┘   └─────────────┐
       │          SUBSCRIBE             │
       ▼                                ▼
┌─────────────┐                  ┌─────────────┐
│ Subscriber  │                  │ Subscriber  │
│  (App 3)    │                  │  (App 4)    │
└─────────────┘                  └─────────────┘
```

## Use Cases for ML Workflows

### 1. Model Training Pipeline
```python
# Training service publishes events
publisher.publish_message('ml_events', {
    'event': 'training_started',
    'model_id': 'xgboost_v2',
    'dataset': 'user_behavior_2024',
    'hyperparameters': {...}
})

# Monitoring service subscribes and tracks progress
```

### 2. Real-time Prediction Alerts
```python
# Prediction service publishes anomalies
publisher.publish_message('alerts', {
    'alert': 'anomaly_detected',
    'model': 'fraud_detector',
    'confidence': 0.97,
    'user_id': '12345'
})

# Security team gets instant notifications
```

### 3. Distributed Model Evaluation
```python
# Multiple evaluation workers subscribe to eval tasks
subscriber.subscribe('eval_tasks')

# Coordinator publishes evaluation jobs
publisher.publish_message('eval_tasks', {
    'task': 'evaluate_model',
    'model_path': 's3://models/v1.2',
    'test_data': 's3://data/test_set'
})
```

### 4. Event Logging & Audit Trail
```python
# All services publish to audit log
publisher.publish_message('audit_log', {
    'service': 'prediction_api',
    'action': 'model_loaded',
    'timestamp': datetime.now().isoformat(),
    'user': 'system'
})

# Audit service subscribes and stores all events
```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_MAX_RETRIES=3
REDIS_RETRY_DELAY=2
```

Load in your code:

```python
import os
from dotenv import load_dotenv

load_dotenv()

publisher = RedisPublisher(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0))
)
```

## Testing

### Test Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### Monitor Redis Activity

In a separate terminal:
```bash
redis-cli monitor
```

This shows all commands being executed in real-time.

### Check Subscriptions

```bash
redis-cli
> PUBSUB CHANNELS
# Lists all active channels

> PUBSUB NUMSUB ml_events
# Shows subscriber count for 'ml_events' channel
```

## Error Handling

Both publisher and subscriber include comprehensive error handling:

- **Connection failures**: Automatic retry with exponential backoff
- **Message serialization errors**: Logged and skipped
- **Handler exceptions**: Caught and logged without crashing subscriber
- **Network interruptions**: Automatic reconnection attempts

## Performance Considerations

### Publisher
- Uses connection pooling for efficiency
- Supports batch publishing to reduce network overhead
- Non-blocking publishes (fire-and-forget pattern)

### Subscriber
- Single-threaded by default for message ordering
- For high throughput, run multiple subscriber instances
- Each subscriber gets a copy of every message (fan-out)

### Scaling Tips

1. **Multiple Subscribers**: Run multiple instances for parallel processing
2. **Channel Partitioning**: Use different channels for different event types
3. **Message Size**: Keep messages small (<1MB recommended)
4. **Connection Pooling**: Reuse connections when publishing frequently

## Monitoring & Debugging

### Logging Levels

Change logging level in the code:
```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
logging.basicConfig(level=logging.WARNING)  # Less verbose
```

### Metrics to Track

- Messages published per second
- Subscriber lag (time between publish and receive)
- Number of active subscribers per channel
- Connection errors and retries

## Troubleshooting

### "Connection refused"
- Ensure Redis is running: `redis-cli ping`
- Check host/port settings
- Verify firewall rules

### "No subscribers received message"
- Subscribers must be connected BEFORE publishing
- Check channel names match exactly (case-sensitive)
- Verify subscriber is running and listening

### Messages not being received
- Check subscriber is subscribed to correct channels
- Ensure subscriber's `listen()` method is called
- Verify network connectivity

## Advanced Features

### Pattern Subscriptions

Subscribe to channels using patterns:
```python
# Subscribe to all ml_* channels
pubsub.psubscribe('ml_*')
```

### Message Filtering

Add filtering logic in handlers:
```python
def filtered_handler(data):
    if data.get('priority') == 'high':
        process_urgent_message(data)
```

### Multiple Publishers

Multiple applications can publish to the same channel:
```python
# Training service
training_publisher.publish_message('ml_events', {...})

# Evaluation service
eval_publisher.publish_message('ml_events', {...})

# Single subscriber receives all messages
```

## Security Considerations

### Redis Authentication

Enable authentication in redis.conf:
```
requirepass your_strong_password
```

Update code:
```python
publisher = RedisPublisher(
    host='localhost',
    port=6379,
    password='your_strong_password'
)
```

### Network Security

- Use TLS for production: `ssl=True, ssl_cert_reqs='required'`
- Restrict Redis to localhost or private network
- Use VPN for remote access
- Enable firewall rules

## License

This implementation is part of the ML Playground repository.

## Contributing

Feel free to submit issues or pull requests for improvements!

## Further Reading

- [Redis Pub/Sub Documentation](https://redis.io/docs/manual/pubsub/)
- [redis-py Documentation](https://redis-py.readthedocs.io/)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
