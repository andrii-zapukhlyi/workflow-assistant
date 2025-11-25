from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.db.db_auth import get_db
from backend.db.crud import get_employee_by_email
from backend.agents.qa_agent import handle_user_query

router = APIRouter()

class QueryRequest(BaseModel):
    user_email: str
    query: str

class QueryResponse(BaseModel):
    answer: str
    links: list[str]

@router.post("/chat_qa", response_model=QueryResponse)
def chat_with_rag(payload: QueryRequest, db: Session = Depends(get_db)):
    employee = get_employee_by_email(db, payload.user_email)
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        answer, links = handle_user_query(
            employee.id,
            payload.query,
            employee.department,
            db
        )
    except Exception as e:
        error_message = str(e)
        if "rate_limit_exceeded" in error_message or "429" in error_message:
            raise HTTPException(
                status_code=429,
                detail=f"LLM rate limit reached. Please try again later.\nOriginal error:\n{error_message}"
            )
        raise HTTPException(status_code=500, detail=f"Internal error:\n{error_message}")
    return QueryResponse(answer=answer, links=links)