# 3.1 задание

from fastapi import FastAPI
from models import UserCreate

app = FastAPI()

@app.post("/create_user")
async def create_user(user: UserCreate):
    return user



#3.2 Задание 

from fastapi import HTTPException

products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.00},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99}
]

@app.get("/product/{product_id}")
async def get_product(product_id: int):
    for product in products:
        if product["product_id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Продукт не найден")

@app.get("/products/search")
async def search_products(
    keyword: str,
    category: str | None = None,
    limit: int = 10
):
    results = []
    for product in products:
        if keyword.lower() in product["name"].lower():
            if category is None or product["category"].lower() == category.lower():
                results.append(product)

    return results[:limit]

# 5.1 задание 

import uuid
from fastapi import Response, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sessions = {}

class LoginData(BaseModel):
    username: str
    password: str

VALID = {"user123":"password123"}

@app.post("/login")
async def login(login_data: LoginData, response: Response):
    if VALID.get(login_data.username) == login_data.password:
        session_token = str(uuid.uuid4())
        sessions[session_token] = login_data.username

        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            max_age=3600
        )
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid")


@app.get("/user")
async def get_user(session_token: str | None = Cookie(default=None)):
    if session_token is None or session_token not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    username = sessions[session_token]
    return {"username": username, "message": "Profile information"}

