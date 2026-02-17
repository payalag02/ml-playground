"""
Redis Subscriber - Production-ready implementation
Subscribes to Redis channels with error handling and message processing
"""

import redis
import json
import logging
import signal
import sys
from typing import Callable, Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RedisSubscriber:
    """Production-ready Redis Subscriber with reconnection and error handling"""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize Redis Subscriber
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            max_retries: Maximum number of connection retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.host = host
        self.port = port
        self.db = db
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.running = False
        self.message_handlers: Dict[str, Callable] = {}
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """Setup graceful shutdown on SIGINT and SIGTERM"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    def connect(self) -> None:
        """Establish connection to Redis with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.redis_client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30
                )
                # Test connection
                self.redis_client.ping()
                self.pubsub = self.redis_client.pubsub()
                logger.info(f"Successfully connected to Redis at {self.host}:{self.port}")
                return
            except redis.ConnectionError as e:
                logger.warning(
                    f"Connection attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )
                if attempt < self.max_retries - 1:
                    import time
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Failed to connect to Redis after all retries")
                    raise
    
    def register_handler(
        self,
        channel: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Register a message handler for a specific channel
        
        Args:
            channel: Channel name
            handler: Callback function that processes messages
        """
        self.message_handlers[channel] = handler
        logger.info(f"Registered handler for channel '{channel}'")
    
    def subscribe(self, *channels: str) -> None:
        """
        Subscribe to one or more channels
        
        Args:
            *channels: Channel names to subscribe to
        """
        if not self.pubsub:
            raise RuntimeError("Not connected to Redis. Call connect() first.")
        
        self.pubsub.subscribe(*channels)
        logger.info(f"Subscribed to channels: {', '.join(channels)}")
    
    def _process_message(self, message: Dict[str, Any]) -> None:
        """
        Process incoming message
        
        Args:
            message: Raw message from Redis
        """
        try:
            if message['type'] == 'message':
                channel = message['channel']
                data = message['data']
                
                # Parse JSON data
                try:
                    parsed_data = json.loads(data)
                except json.JSONDecodeError:
                    parsed_data = {'raw_data': data}
                
                logger.info(f"Received message on '{channel}': {str(parsed_data)[:100]}...")
                
                # Call registered handler if exists
                if channel in self.message_handlers:
                    try:
                        self.message_handlers[channel](parsed_data)
                    except Exception as e:
                        logger.error(f"Error in handler for '{channel}': {e}")
                else:
                    # Default handling - just log
                    self._default_handler(channel, parsed_data)
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _default_handler(self, channel: str, data: Dict[str, Any]) -> None:
        """Default message handler when no custom handler is registered"""
        logger.info(f"[{channel}] {json.dumps(data, indent=2)}")
    
    def listen(self, timeout: Optional[int] = None) -> None:
        """
        Start listening for messages
        
        Args:
            timeout: Optional timeout in seconds for listen loop
        """
        if not self.pubsub:
            raise RuntimeError("Not connected to Redis. Call connect() first.")
        
        self.running = True
        logger.info("Starting message listener...")
        
        try:
            for message in self.pubsub.listen():
                if not self.running:
                    logger.info("Stopping listener...")
                    break
                
                self._process_message(message)
                
        except redis.ConnectionError as e:
            logger.error(f"Connection lost: {e}")
            self.running = False
        except Exception as e:
            logger.error(f"Unexpected error in listener: {e}")
            self.running = False
    
    def close(self) -> None:
        """Close Redis connection and cleanup"""
        self.running = False
        
        if self.pubsub:
            self.pubsub.unsubscribe()
            self.pubsub.close()
            logger.info("Unsubscribed from all channels")
        
        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis connection closed")


# Example message handlers for ML events
def handle_training_event(data: Dict[str, Any]) -> None:
    """Handler for model training events"""
    event = data.get('event', 'unknown')
    model_name = data.get('model_name', 'N/A')
    logger.info(f"🚀 Training Event: {event} for model '{model_name}'")
    
    if 'parameters' in data:
        logger.info(f"   Parameters: {data['parameters']}")


def handle_evaluation_event(data: Dict[str, Any]) -> None:
    """Handler for model evaluation events"""
    if data.get('event') == 'model_evaluation':
        model_name = data.get('model_name', 'N/A')
        accuracy = data.get('accuracy', 0)
        logger.info(f"📊 Evaluation: {model_name} - Accuracy: {accuracy:.2%}")


def handle_prediction_event(data: Dict[str, Any]) -> None:
    """Handler for prediction events"""
    if data.get('event') == 'prediction_request':
        model_id = data.get('model_id', 'N/A')
        features = data.get('input_features', [])
        logger.info(f"🔮 Prediction Request: Model {model_id}, Features: {features}")


def handle_alert(data: Dict[str, Any]) -> None:
    """Handler for alert messages"""
    if 'alert' in data:
        alert_type = data.get('alert')
        service = data.get('service', 'N/A')
        logger.warning(f"⚠️  ALERT: {alert_type} in {service}")
        
        if 'error_rate' in data:
            logger.warning(f"   Error Rate: {data['error_rate']:.2%}")


def main():
    """Example usage of RedisSubscriber"""
    
    # Initialize subscriber
    subscriber = RedisSubscriber(host='localhost', port=6379)
    
    try:
        # Connect to Redis
        subscriber.connect()
        
        # Register custom handlers for different event types
        subscriber.register_handler('ml_events', handle_training_event)
        subscriber.register_handler('notifications', handle_alert)
        
        # Subscribe to channels
        subscriber.subscribe('ml_events', 'notifications', 'audit_log')
        
        # Start listening
        logger.info("Subscriber is ready and listening for messages...")
        logger.info("Press Ctrl+C to stop")
        subscriber.listen()
        
    except KeyboardInterrupt:
        logger.info("Subscriber interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        subscriber.close()


if __name__ == '__main__':
    main()
