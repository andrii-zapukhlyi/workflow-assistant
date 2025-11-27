from backend.db.models import Employee, ChatHistory, ChatSession, RefreshToken
from sqlalchemy.orm import Session
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import datetime


def create_employee(db: Session, full_name: str, email: str, password: str, position: str, department: str) -> Employee:
    employee = Employee(
        full_name=full_name,
        email=email,
        password=password,
        position=position,
        department=department
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def get_employee_by_email(db: Session, email: str) -> Employee | None:
    employee = db.query(Employee).filter(Employee.email == email).first()
    return employee


def get_session_by_id(db: Session, session_id: int) -> ChatSession | None:
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()


def get_sessions_for_user(db, user_id: int) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.last_active.desc())
        .all()
    )


def create_session(db: Session, user_id: int, name: str | None) -> ChatSession:
    session = ChatSession(user_id=user_id, name=name)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session_id: int):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()


def rename_session(db: Session, session_id: int, new_name: str) -> ChatSession | None:
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        session.name = new_name
        db.commit()

    return session


def load_chat_history(session: ChatSession) -> list[BaseMessage]:
    messages = []
    for msg in session.messages:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))
    return messages


def save_messages(db: Session, session: ChatSession, messages: list[BaseMessage]):
    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        else:
            continue
        db_msg = ChatHistory(session_id=session.id, role=role, content=msg.content)
        db.add(db_msg)
    session.last_active = datetime.datetime.now(datetime.timezone.utc)
    db.commit()


def ensure_session_ownership(db: Session, session_id: int, user_id: int) -> ChatSession | None:
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()
    return session


def create_refresh_token(db: Session, user_id: int, token: str, expires_at: datetime.datetime) -> RefreshToken:
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.commit()

    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def get_refresh_token(db: Session, hashed_token: str) -> RefreshToken | None:
    return db.query(RefreshToken).filter(RefreshToken.token == hashed_token).first()


def delete_refresh_token(db: Session, hashed_token: str):
    db.query(RefreshToken).filter(RefreshToken.token == hashed_token).delete()
    db.commit()


def get_user_by_refresh_token(db: Session, token_db: RefreshToken) -> Employee | None:
    return db.query(Employee).filter(Employee.id == token_db.user_id).first()