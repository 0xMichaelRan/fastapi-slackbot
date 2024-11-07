from fastapi import FastAPI, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from dotenv import load_dotenv
import os
import threading
import logging
from typing import Dict, Any

from broker import producer
from broker.consumer import start_consumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get the main logger
logger = logging.getLogger(__name__)

# Configure module-specific logging levels
LOGGING_CONFIG = {
    "pika": logging.WARNING,
    "pika.heartbeat": logging.INFO,
    "pika.adapters": logging.WARNING,
    "pika.connection": logging.INFO,
    "pika.channel": logging.INFO,
    "broker": logging.INFO, 
}

# Apply logging configuration
for logger_name, level in LOGGING_CONFIG.items():
    logging.getLogger(logger_name).setLevel(level)

# Load environment variables
load_dotenv()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(title="Slack Bot API")

    # Initialize Slack app
    slack_app = App(
        token=os.environ.get("SLACK_BOT_TOKEN"),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    )

    handler = SlackRequestHandler(slack_app)

    # FastAPI routes
    @app.get("/")
    async def main_route():
        return {"message": "Hey, It is Wei"}

    @app.post("/slack/events")
    async def slack_events(request: Request):
        return await handler.handle(request)

    def process_slack_event(event: Dict[str, Any], response_handler: Any) -> None:
        """
        Process Slack events and publish messages to queue

        Args:
            event: Slack event data
            response_handler: Function to handle error responses (say or logger.error)
        """
        message_body = {
            "prompt": event["text"],
            "user": event["user"],
            "channel": event["channel"],
            "thread_ts": event["ts"],
        }

        if not producer.publish_message(message_body=message_body):
            error_msg = "Sorry, I couldn't process your message at the moment. Please try again later."
            if hasattr(response_handler, "__call__"):
                response_handler(text=error_msg, thread_ts=event["ts"])
            else:
                logger.error(error_msg)

    # invoked whenever our bot is mentioned on Slack
    @slack_app.event("app_mention")
    def handle_app_mention(event: Dict[str, Any], say: Any) -> None:
        process_slack_event(event, say)

    # invoked whenever a message is posted in any of the channels our bot has been added to
    @slack_app.event("message")
    def handle_message_events(body: Dict[str, Any], logger: Any) -> None:
        process_slack_event(body["event"], logger.error)

    # Start consumer thread on startup
    @app.on_event("startup")
    def startup_event():
        consumer_thread = threading.Thread(
            target=start_consumer, daemon=True, name="RabbitMQ-Consumer"
        )
        consumer_thread.start()
        logger.info("RabbitMQ consumer thread started")

    return app


# Create FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
