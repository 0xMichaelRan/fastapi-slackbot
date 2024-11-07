import pika
import os
import logging
import json
from dotenv import load_dotenv
from slack_bolt import App

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Slack App
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

def post_response_to_slack(slack_message, slack_channel, thread_ts):
    message = f"\n {slack_message} \n"
    slack_app.client.chat_postMessage(
        channel=slack_channel,
        text=message,
        thread_ts=thread_ts
    )

def callback(ch, method, properties, body):
    """ 
    The logic for sending messages to Open API and posting the 
    response to Slack
    """
    body = json.loads(body.decode('utf-8'))
    chatgpt_prompt = body.get("prompt")
    slack_channel = body.get("channel")
    thread_ts = body.get("thread_ts")
    
    # Generate ChatGPT response to user prompt
    chatgpt_response = "Here's a code recommendation for your prompt: " + chatgpt_prompt

    # Send code recommendation to Slack
    post_response_to_slack(
        slack_message=chatgpt_response, 
        slack_channel=slack_channel,
        thread_ts=thread_ts
    )

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    url = os.environ.get('RABBITMQ_URL')
    if not url:
        logger.error("RABBITMQ_URL not found in environment variables")
        return

    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue='slack_messages', durable=True)
    channel.basic_consume(queue='slack_messages', on_message_callback=callback)

    logger.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()