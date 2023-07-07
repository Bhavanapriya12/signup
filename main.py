from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field,EmailStr,validator
from database import engine, SessionLocal
import models
from models import User
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI()

origins =[
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(bind=engine)


class UserCreate(BaseModel):
    username:str
    password:str=Field(min_length=10)

    @validator('password')
    def validate_password(cls,value):
        special_chars=r"[!@#$%^&*()<>.,?/':;|']"
        if not re.search(special_chars,value):
            raise ValueError("password must contain atleast one special character")
        if not any(char.isupper() for char in value):
            raise ValueError("password must contain atleast one uppercase character")
        if not any(char.islower() for char in value):
            raise ValueError("password must contain atleast one lowercase character")
        return value

    email:EmailStr


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