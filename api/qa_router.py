from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.db_auth import get_db
from db.crud import get_employee_by_email
from agents.qa_agent import handle_user_query

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
        raise HTTPException(status_code=500, detail=str(e))

    return QueryResponse(answer=answer, links=links)