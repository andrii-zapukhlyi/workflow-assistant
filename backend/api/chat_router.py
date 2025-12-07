from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.crud import create_session, delete_session, rename_session, get_sessions_for_user, ensure_session_ownership
from agents.qa_agent import handle_user_query
from db.db_auth import get_db
from auth.auth import get_current_user
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config.settings import GROQ_API_KEY
from pydantic import BaseModel

router = APIRouter()

class RenameChatRequest(BaseModel):
    new_name: str


class AskRequest(BaseModel):
    query: str

def generate_session_name(first_message: str) -> str:
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.3-70b-versatile"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Generate a short title (max 5 words) summarizing the user's message. "
         "Do NOT add new information. Keep it concise, neutral, and lowercase."),
        ("user", first_message)
    ])

    response = llm.invoke(prompt.format_messages())
    title = response.content.strip()

    if not title:
        title = first_message[:8] + "..."

    return title.capitalize()


@router.post("/chats")
def create_chat(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = create_session(db, current_user.id, None)
    return {"session_id": session.id, "name": None}


@router.delete("/chats/{session_id}")
def delete_chat(session_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = ensure_session_ownership(db, session_id, current_user.id)
    if not session:
        raise HTTPException(403, "Access denied to this chat session")
    delete_session(db, session_id)
    return {"detail": "Chat session deleted"}


@router.put("/chats/{session_id}/rename")
def rename_chat(session_id: int, req: RenameChatRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = ensure_session_ownership(db, session_id, current_user.id)
    if not session:
        raise HTTPException(403, "Access denied to this chat session")
    renamed_session = rename_session(db, session_id, req.new_name)
    return {"id": renamed_session.id, "name": renamed_session.name}


@router.get("/chats")
def list_chats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = get_sessions_for_user(db, current_user.id)
    return [{"id": s.id, "name": s.name} for s in sessions]


@router.get("/chats/{session_id}/messages")
def get_chat_messages(session_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = ensure_session_ownership(db, session_id, current_user.id)
    if not session:
        raise HTTPException(403, "Access denied to this chat session")
    return [
        {
            "id": m.id,
            "chat_id": session.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in session.messages
    ]


@router.post("/chats/{session_id}/ask")
def ask_in_chat(session_id: int, req: AskRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    session = ensure_session_ownership(db, session_id, current_user.id)
    if not session:
        raise HTTPException(403, "Access denied to this chat session")

    try:
        answer, links = handle_user_query(session_id, req.query, current_user.department, db)
    except Exception as e:
        msg = str(e)
        if "rate_limit_exceeded" in msg or "429" in msg:
            raise HTTPException(429, f"Rate limit. Try later.\n{msg}")
        raise HTTPException(500, f"Internal error: {msg}")

    if not session.name:
        session.name = generate_session_name(req.query)
        db.commit()

    return {"answer": answer, "links": links, "session_name": session.name}