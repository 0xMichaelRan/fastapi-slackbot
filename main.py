from fastapi import FastAPI  
app = FastAPI()   
@app.get("/") 
async def main_route():     
  return {"message": "Hey, this is 0xMichaelRanr"}

# Reference: https://medium.com/@caetanoog/start-your-first-fastapi-server-with-poetry-in-10-minutes-fef90e9604d9
