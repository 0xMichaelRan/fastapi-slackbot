from fastapi import FastAPI, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from dotenv import load_dotenv
import os

from broker import cloudamqp

# Load environment variables from a .env file
load_dotenv()

# Initialize FastAPI and Slack apps
app = FastAPI()
slack_app = App(
    token=os.environ.get(
        "SLACK_BOT_TOKEN"
    ),  # Slack bot token from environment variables
    signing_secret=os.environ.get(
        "SLACK_SIGNING_SECRET"
    ),  # Slack signing secret from environment variables
)
handler = SlackRequestHandler(slack_app)  # Create a request handler for Slack events


# FastAPI routes
@app.get("/")
async def main_route():
    # Define a simple GET route that returns a welcome message
    return {"message": "Hey, It is Wei"}


@app.post("/slack/events")
async def slack_events(request: Request):
    # Define a POST route to handle Slack events
    return await handler.handle(request)


# Slack event handlers
@slack_app.event("app_mention")
def handle_app_mention(event, say) -> None:
    # This handler is invoked whenever our bot is mentioned on Slack.
    message = event["text"]  # Extract the message text
    user = event["user"]  # Extract the user ID
    channel = event["channel"]  # Extract the channel ID
    thread_ts = event["ts"]  # Extract the thread timestamp

    # Publish the message to a message broker
    success = cloudamqp.publish_message(
        message_body={
            "prompt": message,
            "user": user,
            "channel": channel,
            "thread_ts": thread_ts,
        }
    )

    if not success:
        # Notify the user if the message couldn't be processed
        say(
            text="Sorry, I couldn't process your message at the moment. Please try again later.",
            thread_ts=thread_ts,
        )


@slack_app.event("message")
def handle_message_events(body, logger):
    # This handler is invoked whenever a message is posted in any of the channels
    # our bot has been added to – it doesn’t matter if it was mentioned or not.
    # For now, the handler does nothing, but it is added anyway to make it easier 
    # to extend the project.
    pass
