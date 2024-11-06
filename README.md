# fastapi-slackbot

## Setup

```bash
poetry init 
poetry add fastapi uvicorn
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

# Slackbot

## Dependencies

```bash
poetry add fastapi uvicorn python-dotenv slack-bolt pika
```

## ngrok

```bash
ngrok http 8000
```

## Run:

```bash
poetry run uvicorn main:app --reload
```