from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
import datetime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    position = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)

    sessions = relationship("ChatSession", back_populates="user")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)  # mandatory
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    last_active = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    user = relationship("Employee", back_populates="sessions")
    messages = relationship("ChatHistory", back_populates="session", cascade="all, delete-orphan")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    session = relationship("ChatSession", back_populates="messages")