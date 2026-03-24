from fastapi import FastAPI, HTTPException, APIRouter, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Annotated
import json
import os

app = FastAPI()
router = APIRouter()


class User(BaseModel):
    username: str
    password: str
    email: EmailStr
    age: Annotated[int, Field(ge=18, le=60, description="Age of the user")]
    phone: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if len(value) < 3 or len(value) > 20:
            raise ValueError("Username must be 3-20 characters long")
        if not value.isalnum():
            raise ValueError("Username must contain only letters and numbers")
        if not value[0].isalpha():
            raise ValueError("Username must start with a letter")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        special_chars = "@#$%^&*"
        if not any(c in special_chars for c in value):
            raise ValueError("Password must contain at least one special character")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if len(value) != 10:
            raise ValueError("Phone number must be 10 digits long")
        if not value.isdigit():
            raise ValueError("Phone number should be numeric")
        return value


def load_data():
    if not os.path.exists('users.json'):
        return {}
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_data(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)


@router.get("/")
def home():
    return {
        "message": "Welcome to the FastAPI Task Manager API",
        "endpoints": {
            "register_user": "POST /users",
            "get_all_users": "GET /users",
            "get_user": "GET /users/{username}",
            "update_user": "PUT /users/{username}",
            "delete_user": "DELETE /users/{username}"
        },
        "docs": "/docs"
    }

@router.get('/users')
def view_users():
    data = load_data()
    # exclude password from all users
    return {
        uid: {k: v for k, v in info.items() if k != "password"}
        for uid, info in data.items()
    }

@router.get('/users/{username}')
def view_user(username: str = Path(..., description="Username in DB", example="vishal123")):
    normalized = username.upper()
    data = load_data()
    if normalized not in data:
        raise HTTPException(status_code=404, detail="User not found")
    user = data[normalized]
    return {
        "email": user["email"],
        "age": user["age"],
        "phone": user["phone"]  
    }

@router.post('/users', status_code=201)
def create_user(user: User):
    username = user.username.upper()
    data = load_data()
    if username in data:
        raise HTTPException(status_code=400, detail="User already exists")
    data[username] = {
        "email": user.email,
        "password": user.password,
        "age": user.age,
        "phone": user.phone
    }
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "User added"})

@router.delete('/users/{username}')
def delete_user(username: str = Path(..., description="Username", example="vishal123")):
    normalized = username.upper()
    data = load_data()
    if normalized not in data:
        raise HTTPException(status_code=404, detail="User not found")
    del data[normalized]
    save_data(data)
    return {"message": "User deleted"}

@router.put('/users/{username}')
def update_user(username: str, user: User):
    normalized = username.upper()
    data = load_data()
    if normalized not in data:
        raise HTTPException(status_code=404, detail="User not found")
    data[normalized] = {
        "email": user.email,
        "password": user.password,
        "age": user.age,
        "phone": user.phone
    }
    save_data(data)
    return {"message": "User updated"}


app.include_router(router)