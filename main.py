from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

# Assuming you have a 'models' module with 'Assign' and 'Base' defined
from models import Base, User, Chat, Message
from database import SessionLocal, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserBase(BaseModel):
    username: str
    name: str
    surname: str
    password: str


class ChatBase(BaseModel):
    user1_id: int
    user2_id: int


class ChatResponseBase(BaseModel):
    id: int
    user1_id: int
    user2_id: int


class MessageBase(BaseModel):
    chat_id: int
    user_id: int
    content: str


class MessageResponseBase(BaseModel):
    chat_id: int
    user_id: int
    content: str
    time: datetime


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users", response_model=UserBase)
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    user_data = user.dict()
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users")
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return {"username": user.username, "name": user.name, "surname": user.surname}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.username == username)
                                 & (User.password == password)).first()
    return user


@app.post("/chats", response_model=ChatBase)
async def create_chat(chat: ChatBase, db: Session = Depends(get_db)):
    chat_data = chat.dict()
    new_chat = Chat(**chat_data)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


@app.get("/chats/", response_model=List[ChatResponseBase])
async def get_chats_by_user_id(id: int, db: Session = Depends(get_db)):
    res = db.query(Chat).filter(
        (Chat.user2_id == id) | (Chat.user1_id == id)).all()
    return res


@app.post("/messages", response_model=MessageBase)
async def create_message(msg: MessageBase, db: Session = Depends(get_db)):
    new_msg = Message(**msg.dict())
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg


@app.get("/messages/", response_model=List[MessageResponseBase])
async def get_messages_by_chat_id(id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.chat_id == id).all()
    return messages
