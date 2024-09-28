import datetime

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def home():
    """
    returns hello world message
    :return: str
    """
    return {"message": "Hello"}


@app.get("/date")
async def date():
    return {"date": datetime.datetime.now()}
