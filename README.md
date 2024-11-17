# fastapi-slackbot

## Setup poetry

```bash
poetry init 
poetry add fastapi uvicorn python-dotenv slack-bolt pika
poetry shell
```

## Run the app
 
```bash
uvicorn main:app --reload
```

## Access the app

 http://127.0.0.1:8000/

## Swagger UI:

 http://127.0.0.1:8000/docs#/

# Slack Setup

## ngrok

Setup ngrok following the instructions [here](https://dashboard.ngrok.com/get-started/setup/macos/).

Then expose port 8000 using ngrok:

```bash
ngrok http 8000
```

You will get a URL like `https://<random>.ngrok.app`. Append `/slack/events` to the URL, it becomes something like `https://3fc4-134-238-32-82.ngrok-free.app/slack/events`. You do not need this URL in your code. 

Now, go to Slackbot's "Event Subscriptions" and paste into "Request URL" field.

Done!
