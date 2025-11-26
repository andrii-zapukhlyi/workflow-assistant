from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.crud import create_session, get_sessions_for_user, ensure_session_ownership
from backend.agents.qa_agent import handle_user_query
from backend.db.db_auth import get_db
from backend.auth.auth import get_current_user

router = APIRouter()

@router.post("/create_chat")
def create_new_chat(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = create_session(db, current_user.id, "new chat")
    return {"session_id": session.id, "name": "new chat"}


@router.get("/chats")
def list_chats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = get_sessions_for_user(db, current_user.id)
    return [{"id": s.id, "name": s.name} for s in sessions]


@router.get("/messages")
def get_chat_messages(session_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = ensure_session_ownership(db, session_id, current_user.id)
    if not session:
        raise HTTPException(403, "Access denied to this chat session")

    return [{"role": m.role, "content": m.content} for m in session.messages]


@router.post("/ask")
def ask_in_chat(session_id: int, query: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    session = ensure_session_ownership(db, session_id, current_user.id)
    if not session:
        raise HTTPException(403, "Access denied to this chat session")

    try:
        answer, links = handle_user_query(session_id, query, current_user.department, db)
    except Exception as e:
        msg = str(e)
        if "rate_limit_exceeded" in msg or "429" in msg:
            raise HTTPException(429, f"Rate limit. Try later.\n{msg}")
        raise HTTPException(500, f"Internal error: {msg}")

    return {"answer": answer, "links": links}