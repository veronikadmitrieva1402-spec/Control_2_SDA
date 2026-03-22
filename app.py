from fastapi import FastAPI, Response, Cookie, HTTPException
from pydantic import BaseModel
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import uuid
import time

app = FastAPI()

from models import UserCreate

@app.post("/create_user")
async def create_user(user: UserCreate):
    return user

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

#5.3 ЗАДАНИЕ

class LoginData(BaseModel):
    username: str
    password: str

VALID = {"user123": "password123"}

SECRET_KEY = "your-secret-key-for-5.3"
serializer = URLSafeTimedSerializer(SECRET_KEY)

users_db = {}

def create_session_token(user_id: str, timestamp: int) -> str:
    
    data = f"{user_id}.{timestamp}"
    return serializer.dumps(data)

def verify_session_token(token: str) -> tuple[str | None, int | None]:
    try:
        data = serializer.loads(token)
        parts = data.split('.')
        if len(parts) == 2:
            return parts[0], int(parts[1])
    except (BadSignature, SignatureExpired, ValueError):
        pass
    return None, None

@app.post("/login")
async def login(login_data: LoginData, response: Response):
    if VALID.get(login_data.username) == login_data.password:
        user_id = str(uuid.uuid4())
        
        users_db[user_id] = login_data.username
        
        current_time = int(time.time())
        
        token = create_session_token(user_id, current_time)
        
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            max_age=300,
            path="/"
        )
        
        return {"message": "Login successful", "user_id": user_id}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/profile")
async def get_profile(
    response: Response,
    session_token: str | None = Cookie(default=None)
):
    
    if session_token is None:
        raise HTTPException(status_code=401, detail="Session expired")
    
    user_id, token_time = verify_session_token(session_token)
    
    if user_id is None or token_time is None:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    username = users_db.get(user_id)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    current_time = int(time.time())
    time_diff = current_time - token_time
    
    print(f"Time since last activity: {time_diff} seconds")
    
    if time_diff > 300:
        raise HTTPException(status_code=401, detail="Session expired")
    
    should_update = False
    update_message = ""
    
    if time_diff >= 180 and time_diff < 300:
        should_update = True
        update_message = "Session extended"
        print("Session extended (3-5 minutes passed)")
    elif time_diff < 180:
        update_message = "Session active (less than 3 minutes)"
        print("Session not extended (less than 3 minutes)")
    else:
        pass
    
    if should_update:
        new_timestamp = current_time
        new_token = create_session_token(user_id, new_timestamp)
        
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=300,
            path="/"
        )
    
    return {
        "user_id": user_id,
        "username": username,
        "message": "Profile information",
        "session_status": update_message,
        "time_since_last_activity": time_diff
    }