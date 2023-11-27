from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Column, Integer, String


class Base(DeclarativeBase, AsyncAttrs):
    pass


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    media = Column(String)
    media_path = Column(String)
    text = Column(String)
    name = Column(String)
    owner = Column(Integer)


class Session(Base):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, unique=True)
    session_string = Column(String)
    user_id = Column(Integer)
    owner = Column(Integer)



class Chat(Base):
    __tablename__ = "chats and bots"

    chat_id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, primary_key=True)


class AllChats(Base):
    __tablename__ = "chats"
    chat_id = Column(Integer, primary_key=True)
