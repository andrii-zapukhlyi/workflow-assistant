from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.crud import (
    get_employee_by_email,
    create_session,
    get_sessions_for_user,
    get_session_by_id,
)
from backend.agents.qa_agent import handle_user_query
from backend.db.db_auth import get_db

router = APIRouter()

@router.post("/create_chat")
def create_new_chat(user_email: str, db: Session = Depends(get_db)):
    employee = get_employee_by_email(db, user_email)
    if not employee:
        raise HTTPException(404, "User not found")

    name = "new chat"
    session = create_session(db, employee.id, name)

    return {"session_id": session.id, "name": name}


@router.get("/list_chats")
def list_chats(user_email: str, db: Session = Depends(get_db)):
    employee = get_employee_by_email(db, user_email)
    if not employee:
        raise HTTPException(404, "User not found")

    sessions = get_sessions_for_user(db, employee.id)

    return [
        {"id": s.id, "name": s.name}
        for s in sessions
    ]


@router.get("/get_chat_messages/")
def get_chat_messages(session_id: int, db: Session = Depends(get_db)):
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(404, "Chat not found")

    return [
        {"role": m.role, "content": m.content}
        for m in session.messages
    ]


@router.post("/ask_in_chat")
def ask_in_chat(session_id: int, query: str, user_email: str, db: Session = Depends(get_db)):
    employee = get_employee_by_email(db, user_email)
    if not employee:
        raise HTTPException(404, "User not found")

    try:
        answer, links = handle_user_query(session_id, query, employee.department, db)
    except Exception as e:
        msg = str(e)
        if "rate_limit_exceeded" in msg or "429" in msg:
            raise HTTPException(429, f"Rate limit. Try later.\n{msg}")
        raise HTTPException(500, f"Internal error: {msg}")

    return {"answer": answer, "links": links}