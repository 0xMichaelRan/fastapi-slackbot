from fastapi import FastAPI, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from dotenv import load_dotenv
import os
import threading
import logging
from typing import Dict, Any, Callable

from broker import producer
from broker.consumer import start_consumer
from config.logging_config import setup_logging

# Setup logging
logger = setup_logging()

# Load environment variables
load_dotenv()


class SlackEventProcessor:
    """Handle Slack event processing and message publishing"""

    @staticmethod
    def process_event(event: Dict[str, Any], response_handler: Callable) -> None:
        """
        Process Slack events and publish messages to queue

        Args:
            event: Slack event data
            response_handler: Function to handle error responses
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


def create_slack_app() -> App:
    """Create and configure Slack app"""
    return App(
        token=os.environ.get("SLACK_BOT_TOKEN"),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    )


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Slack Bot API",
        description="A FastAPI application for handling Slack events",
        version="1.0.0",
    )

    # Initialize Slack app and handler
    slack_app = create_slack_app()
    handler = SlackRequestHandler(slack_app)
    processor = SlackEventProcessor()

    @app.get("/")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "message": "Hey, It is 0xMichaelRan"}

    @app.post("/slack/events")
    async def slack_events(request: Request):
        """Handle incoming Slack events"""
        return await handler.handle(request)

    @slack_app.event("app_mention")
    def handle_app_mention(event: Dict[str, Any], say: Callable) -> None:
        """Handle mentions of the bot in Slack"""
        processor.process_event(event, say)

    @slack_app.event("message")
    def handle_message_events(body: Dict[str, Any], logger: Any) -> None:
        """Handle messages in channels where the bot is present"""
        processor.process_event(body["event"], logger.error)

    @app.on_event("startup")
    def startup_event():
        """Start the RabbitMQ consumer thread when the application starts"""
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
