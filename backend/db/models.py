from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
import datetime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    full_name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    department = Column(Text, nullable=False)
    position_id = Column(Integer, ForeignKey("positions_skills.id", ondelete="SET NULL"), nullable=True)

    position_obj = relationship("PositionsSkills", back_populates="employees")
    sessions = relationship("ChatSession", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, default=None, nullable=True)
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

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"))
    token = Column(String(255), unique=True, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    user = relationship("Employee", back_populates="refresh_tokens")

class PositionsSkills(Base):
    __tablename__ = "positions_skills"
    id = Column(Integer, primary_key=True)
    position = Column(Text, unique=True, nullable=False)
    position_level = Column(Text, nullable=False)
    skills = Column(JSON, nullable=False)

    employees = relationship("Employee", back_populates="position_obj")