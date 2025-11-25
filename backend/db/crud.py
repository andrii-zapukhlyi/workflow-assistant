from backend.db.models import Employee, ChatHistory, ChatSession
from sqlalchemy.orm import Session
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import datetime
from sqlalchemy import text

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

def get_employee_by_email(db: Session, email: str) -> Employee | None:
    employee = db.query(Employee).filter(Employee.email == email).first()
    return employee

def get_session_by_id(db: Session, session_id: int) -> ChatSession | None:
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def get_sessions_for_user(db, user_id: int):
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.last_active.desc())
        .all()
    )

def create_session(db: Session, user_id: int, name: str) -> ChatSession:
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

def clear_chat_sessions(db: Session):
    db.execute(text("DELETE FROM chat_sessions"))
    db.commit()
    seq_name = db.execute(text("""SELECT pg_get_serial_sequence('chat_sessions', 'id')""")).scalar()
    db.execute(text(f"""SELECT setval('{seq_name}', COALESCE((SELECT MAX(id) FROM chat_sessions), 1), false);"""))
    db.commit()
    return

def clear_chat_history(db: Session):
    db.execute(text("DELETE FROM chat_history"))
    db.commit()
    seq_name = db.execute(text("""SELECT pg_get_serial_sequence('chat_history', 'id')""")).scalar()
    db.execute(text(f"""SELECT setval('{seq_name}', COALESCE((SELECT MAX(id) FROM chat_history), 1), false);"""))
    db.commit()
    return