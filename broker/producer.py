import json
import os
import pika
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def publish_message(message_body: dict) -> bool:
    """
    Publishes a message to RabbitMQ with error handling
    Returns: bool indicating success/failure
    """
    url = os.environ.get('RABBITMQ_URL')
    if not url:
        logger.error("RABBITMQ_URL not found in environment variables")
        return False

    try:
        # Configure connection parameters
        params = pika.URLParameters(url)
        
        # Establish connection
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        # Declare queue (with durable=True for message persistence)
        channel.queue_declare(queue='slack_messages', durable=True)
        
        # Publish message with delivery confirmation
        channel.basic_publish(
            exchange='',
            routing_key='slack_messages',
            body=json.dumps(message_body),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        
        logger.info(f"Successfully published message for user: {message_body.get('user')}")
        connection.close()
        return True

    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
        return False
    except pika.exceptions.AMQPChannelError as e:
        logger.error(f"Channel error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while publishing message: {str(e)}")
        return False