from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Literal, Annotated
import json
import os


router = APIRouter()


class User(BaseModel):
  username: str
  
  @field_validator("username")
  def validate_username(cls, value):
    
    # Rule 1: Length
    if len(value) < 3 or len(value) > 20:
      raise ValueError("Username must be 3-20 characters long")
    
    # Rule 2: Only letters + numbers
    if not value.isalnum():
      raise ValueError("Username must contain only letters and numbers")
    
    # Rule 3: Must start with a letter
    if not value[0].isalpha():
      raise ValueError("Username must start with a letter")
  
    return value
  
  
  password: str
  
  @field_validator("password")
  def validate_password(cls, value):
    # Rule 1: Length
    if len(value) < 8:
      raise ValueError("Password must be at least 8 characters long")
    
    # Rule 2: At least one uppercase
    if not any(c.isupper() for c in value):
      raise ValueError("Password must contain atleast one uppercase letter")
  
    # Rule 3: At least one lowercase
    if not any(c.islower() for c in value):
      raise ValueError("Password must contain at least one lowercase letter")
    
    # Rule 4: At least one digit
    if not any(c.isdigit() for c in value):
      raise ValueError("Password must contain at least one digit")
    
    # Rule 5: At least one special character
    special_chars = "@#$%^&*"
    if not any(c in special_chars for c in value):
      raise ValueError("Password must contain atleast one special character")
    
    return value
  
  email: EmailStr
  age: Annotated[int, Field(ge=18, le=60, description="Age of the user")]
  phone: str
  
  @field_validator("phone")
  def validate_phone(cls, value):
    # Rule 1: Length
    if len(value) != 10:
      raise ValueError("Phone number must be 10 digit long")
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
        "description": "Backend service for user registration and task management.",
        "endpoints": {
            "register_user": "POST /users",
            "create_task": "POST /tasks",
            "get_tasks": "GET /tasks/{username}"
        },
        "docs": "/docs"
    }
    
@router.get('/users')
def view_users():
  users = load_data()
  
  return users
    
@router.post('/users')
async def create_user(user: User):
  username= user.username.upper()
  
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
  
  return JSONResponse(status_code=201, content={"message":"User added"})
