from db.models import Employee, ChatHistory, ChatSession, RefreshToken, PositionsSkills
from sqlalchemy.orm import Session
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import datetime
from typing import List
from sqlalchemy.dialects.postgresql import JSONB



## ----- Employee CRUD -----


def create_employee(db: Session, full_name: str, email: str, password: str, position_id: int, department: str) -> Employee:
    employee = Employee(
        full_name=full_name,
        email=email,
        password=password,
        position_id=position_id,
        department=department,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def get_employee_by_email(db: Session, email: str) -> Employee | None:
    return db.query(Employee).filter(Employee.email == email).first()


def get_employees_by_skills(db: Session, skills: list[str]):
    return (
        db.query(Employee)
        .join(PositionsSkills, Employee.position_id == PositionsSkills.id)
        .filter(PositionsSkills.skills.cast(JSONB).contains(skills))
        .all()
    )

## ----- Sessions CRUD -----


def get_session_by_id(db: Session, session_id: int) -> ChatSession | None:
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()


def get_sessions_for_user(db, user_id: int) -> List[ChatSession]:
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

def ensure_session_ownership(db: Session, session_id: int, user_id: int) -> ChatSession | None:
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()
    return session


## ----- Chat History CRUD -----


def load_chat_history(session: ChatSession) -> List[BaseMessage]:
    messages = []
    for msg in session.messages:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))
    return messages


def save_messages(db: Session, session: ChatSession, messages: List[BaseMessage]):
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


## ----- Refresh Token CRUD -----


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

## ----- Positions Skills CRUD -----

def create_position_skill(db: Session, position: str, position_level: str, skills: List[str]) -> PositionsSkills:
    pos_skill = PositionsSkills(position=position, position_level=position_level, skills=skills)
    db.add(pos_skill)
    db.commit()
    db.refresh(pos_skill)
    return pos_skill

def get_current_positions_levels(db: Session) -> List[tuple[str, str]]:
    result = db.query(PositionsSkills.position, PositionsSkills.position_level).distinct().all()
    return [(pos, lvl) for pos, lvl in result]

def get_position_by_name_level(db: Session, position: str, position_level: str) -> PositionsSkills | None:
    return db.query(PositionsSkills).filter(PositionsSkills.position == position and PositionsSkills.position_level == position_level).first()