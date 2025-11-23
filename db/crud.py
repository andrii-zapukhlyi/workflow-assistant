from .models import Employee, ChatHistory, ChatSession
from sqlalchemy.orm import Session
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import datetime

def create_employee(db: Session, full_name: str, email: str, password: str, position: str, department: str) -> Employee:
    new_employee = Employee(
        full_name=full_name,
        email=email,
        password=password,
        position=position,
        department=department
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

def get_employee_by_email(db, email: str) -> Employee | None:
    employee = db.query(Employee).filter(Employee.email == email).first()
    if not employee:
        raise ValueError("Employee with the given email does not exist.")
    return employee

def get_latest_session(user_id: int, db: Session) -> ChatSession | None:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.last_active.desc())
        .first()
    )

def create_session(user_id: int, name: str, db: Session) -> ChatSession:
    session = ChatSession(user_id=user_id, name=name)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def load_chat_history(session: ChatSession) -> list[BaseMessage]:
    messages = []
    for msg in session.messages:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))
    return messages

def save_messages(session: ChatSession, messages: list[BaseMessage], db: Session):
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