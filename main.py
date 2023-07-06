from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,validator,Field
from database import engine, SessionLocal
import models
from models import User
import re

app = FastAPI()


models.Base.metadata.create_all(bind=engine)


class UserCreate(BaseModel):
    username:str
    password:str=Field(min_length=8)
    email:str

    @validator('email')
    def validate_email(email):
        if not email.endswith('@gmail.com'):
            raise ValueError('only Gmail addresses are allowed')
        return email


class UserLogin(BaseModel):
    username:str
    password:str


@app.post("/signup")
async def signup(user: UserCreate):

    db=SessionLocal()
    existing_user= db.query(User).filter(User.email==user.email).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="user already exists")
    new_user= User(username=user.username,password=user.password,email=user.email)
    db.add(new_user)
    db.commit()

    return{"message":"User created successfully"}


@app.post("/login")
async def login(user: UserLogin):
    db=SessionLocal()

    existing_user=db.query(User).filter(User.username==user.username).first()
    if not user or not verify_password(user.password,existing_user.password):
        raise HTTPException(status_code=401,detail="Incorrect username or password")
    return{"message": "Login successful"}


def verify_password(plain_password,password):

    return plain_password == password