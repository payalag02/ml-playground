"""
Redis Publisher - Production-ready implementation
Publishes messages to Redis channels with error handling and retry logic
"""

import redis
import json
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RedisPublisher:
    """Production-ready Redis Publisher with connection pooling and error handling"""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        max_retries: int = 3,
        retry_delay: int = 1
    ):
        """
        Initialize Redis Publisher
        
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
        self._connect()
    
    def _connect(self) -> None:
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
                logger.info(f"Successfully connected to Redis at {self.host}:{self.port}")
                return
            except redis.ConnectionError as e:
                logger.warning(
                    f"Connection attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Failed to connect to Redis after all retries")
                    raise
    
    def publish_message(
        self,
        channel: str,
        message: Dict[str, Any],
        add_timestamp: bool = True
    ) -> bool:
        """
        Publish a message to a Redis channel
        
        Args:
            channel: Channel name to publish to
            message: Message dictionary to publish
            add_timestamp: Whether to add timestamp to message
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        try:
            if add_timestamp:
                message['timestamp'] = datetime.now().isoformat()
            
            message_json = json.dumps(message)
            
            # Publish returns the number of subscribers that received the message
            subscribers = self.redis_client.publish(channel, message_json)
            
            logger.info(
                f"Published to '{channel}': {message_json[:100]}... "
                f"(received by {subscribers} subscriber(s))"
            )
            return True
            
        except redis.RedisError as e:
            logger.error(f"Error publishing message to '{channel}': {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Error serializing message: {e}")
            return False
    
    def publish_batch(
        self,
        channel: str,
        messages: list[Dict[str, Any]],
        delay: float = 0.1
    ) -> tuple[int, int]:
        """
        Publish multiple messages to a channel
        
        Args:
            channel: Channel name to publish to
            messages: List of message dictionaries
            delay: Delay between messages in seconds
            
        Returns:
            tuple: (successful_count, failed_count)
        """
        successful = 0
        failed = 0
        
        for msg in messages:
            if self.publish_message(channel, msg):
                successful += 1
            else:
                failed += 1
            
            if delay > 0:
                time.sleep(delay)
        
        logger.info(
            f"Batch publish complete: {successful} successful, {failed} failed"
        )
        return successful, failed
    
    def close(self) -> None:
        """Close Redis connection"""
        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis connection closed")


def main():
    """Example usage of RedisPublisher"""
    
    # Initialize publisher
    publisher = RedisPublisher(host='localhost', port=6379)
    
    try:
        # Example 1: Publish a single message
        message = {
            'event': 'model_training_started',
            'model_name': 'random_forest_classifier',
            'parameters': {
                'n_estimators': 100,
                'max_depth': 10
            }
        }
        publisher.publish_message('ml_events', message)
        
        # Example 2: Publish multiple messages
        messages = [
            {
                'event': 'data_processed',
                'dataset': 'iris',
                'rows': 150,
                'status': 'success'
            },
            {
                'event': 'model_evaluation',
                'model_name': 'logistic_regression',
                'accuracy': 0.95,
                'f1_score': 0.93
            },
            {
                'event': 'prediction_request',
                'model_id': 'model_v1.2',
                'input_features': [5.1, 3.5, 1.4, 0.2]
            }
        ]
        
        publisher.publish_batch('ml_events', messages, delay=0.5)
        
        # Example 3: Publish to multiple channels
        channels = ['ml_events', 'notifications', 'audit_log']
        alert_message = {
            'alert': 'high_error_rate',
            'service': 'prediction_api',
            'error_rate': 0.15
        }
        
        for channel in channels:
            publisher.publish_message(channel, alert_message)
        
    except KeyboardInterrupt:
        logger.info("Publisher interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        publisher.close()


if __name__ == '__main__':
    main()
