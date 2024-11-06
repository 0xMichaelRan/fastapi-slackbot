from fastapi import FastAPI, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from dotenv import load_dotenv
import os
import threading
import logging

from broker import producer
from broker.consumer import start_consumer

# Load environment variables
load_dotenv()

# Initialize FastAPI and Slack apps
app = FastAPI()
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)
handler = SlackRequestHandler(slack_app)

# FastAPI routes
@app.get("/")
async def main_route():
    return {"message": "Hey, It is Wei"}

@app.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)

# Slack event handlers
@slack_app.event("app_mention")
def handle_app_mention(event, say) -> None:
    message = event["text"]
    user = event["user"]
    channel = event["channel"]
    thread_ts = event["ts"]

    success = producer.publish_message(
        message_body={
            "prompt": message,
            "user": user,
            "channel": channel,
            "thread_ts": thread_ts
        }
    )

    if not success:
        say(
            text="Sorry, I couldn't process your message at the moment. Please try again later.",
            thread_ts=thread_ts
        )

@slack_app.event("message")
def handle_message_events(body, logger):
    event = body["event"]
    message = event["text"]
    user = event["user"]
    channel = event["channel"]
    thread_ts = event["ts"]

    success = producer.publish_message(
        message_body={
            "prompt": message,
            "user": user,
            "channel": channel,
            "thread_ts": thread_ts
        }
    )

    if not success:
        logger.error(
            text="Sorry, I couldn't process your message at the moment. Please try again later.",
            thread_ts=thread_ts
        )
    pass

# Start the consumer in a separate thread
@app.on_event("startup")
def startup_event():
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
