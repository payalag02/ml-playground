"""
Integration test for Redis Pub/Sub
Demonstrates end-to-end functionality
"""

import time
import threading
from publisher import RedisPublisher
from subscriber import RedisSubscriber
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestSubscriber:
    """Test subscriber that collects messages"""
    
    def __init__(self):
        self.received_messages = []
        self.subscriber = RedisSubscriber()
        self.thread = None
    
    def message_handler(self, data):
        """Store received messages"""
        self.received_messages.append(data)
        logger.info(f"✓ Received message: {data.get('event', 'unknown')}")
    
    def start(self, channel):
        """Start subscriber in background thread"""
        self.subscriber.connect()
        self.subscriber.register_handler(channel, self.message_handler)
        self.subscriber.subscribe(channel)
        
        def listen_thread():
            self.subscriber.listen()
        
        self.thread = threading.Thread(target=listen_thread, daemon=True)
        self.thread.start()
        logger.info(f"Test subscriber started on channel '{channel}'")
    
    def stop(self):
        """Stop subscriber"""
        self.subscriber.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self.subscriber.close()
        logger.info("Test subscriber stopped")


def run_integration_test():
    """Run complete integration test"""
    
    logger.info("="*60)
    logger.info("Starting Redis Pub/Sub Integration Test")
    logger.info("="*60)
    
    # Test channel
    test_channel = 'integration_test'
    
    # Start subscriber
    logger.info("\n[1/5] Starting subscriber...")
    test_sub = TestSubscriber()
    test_sub.start(test_channel)
    time.sleep(2)  # Give subscriber time to connect
    
    # Create publisher
    logger.info("\n[2/5] Creating publisher...")
    publisher = RedisPublisher()
    time.sleep(1)
    
    # Test 1: Single message
    logger.info("\n[3/5] Test 1: Publishing single message...")
    message1 = {
        'test': 'single_message',
        'event': 'test_event_1',
        'data': 'Hello, Redis!'
    }
    publisher.publish_message(test_channel, message1)
    time.sleep(1)
    
    # Test 2: Batch messages
    logger.info("\n[4/5] Test 2: Publishing batch messages...")
    batch_messages = [
        {'test': 'batch', 'event': 'batch_event_1', 'sequence': 1},
        {'test': 'batch', 'event': 'batch_event_2', 'sequence': 2},
        {'test': 'batch', 'event': 'batch_event_3', 'sequence': 3},
    ]
    publisher.publish_batch(test_channel, batch_messages, delay=0.2)
    time.sleep(2)
    
    # Test 3: ML workflow simulation
    logger.info("\n[5/5] Test 3: Simulating ML workflow...")
    ml_messages = [
        {
            'event': 'data_loaded',
            'dataset': 'test_dataset',
            'rows': 1000,
            'columns': 10
        },
        {
            'event': 'preprocessing_complete',
            'features_created': 15,
            'missing_values_handled': True
        },
        {
            'event': 'model_training_started',
            'model_type': 'RandomForest',
            'hyperparameters': {'n_estimators': 100, 'max_depth': 10}
        },
        {
            'event': 'model_training_complete',
            'duration_seconds': 45.2,
            'final_loss': 0.023
        },
        {
            'event': 'model_evaluation',
            'accuracy': 0.94,
            'f1_score': 0.92,
            'auc_roc': 0.96
        }
    ]
    
    for msg in ml_messages:
        publisher.publish_message(test_channel, msg)
        time.sleep(0.5)
    
    time.sleep(2)
    
    # Verify results
    logger.info("\n" + "="*60)
    logger.info("Test Results")
    logger.info("="*60)
    
    total_expected = 1 + len(batch_messages) + len(ml_messages)
    total_received = len(test_sub.received_messages)
    
    logger.info(f"Expected messages: {total_expected}")
    logger.info(f"Received messages: {total_received}")
    
    if total_received == total_expected:
        logger.info("✓ SUCCESS: All messages received!")
    else:
        logger.warning(f"⚠ WARNING: Missing {total_expected - total_received} messages")
    
    # Show received events
    logger.info("\nReceived events:")
    for i, msg in enumerate(test_sub.received_messages, 1):
        event = msg.get('event', 'unknown')
        logger.info(f"  {i}. {event}")
    
    # Cleanup
    logger.info("\nCleaning up...")
    test_sub.stop()
    publisher.close()
    
    logger.info("\n" + "="*60)
    logger.info("Integration Test Complete!")
    logger.info("="*60)


if __name__ == '__main__':
    try:
        run_integration_test()
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
