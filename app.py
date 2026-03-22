# 3.1 задание

from fastapi import FastAPI
from models import UserCreate

app = FastAPI()

@app.post("/create_user")
async def create_user(user: UserCreate):
    return user