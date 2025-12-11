from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.db_auth import get_db
from db.crud import get_employee_by_email, create_employee, create_refresh_token, get_refresh_token, get_user_by_refresh_token, delete_refresh_token, get_current_positions_levels, get_position_by_name_level, create_position_skill
from auth.auth import verify_password, create_access_token, hash_password, hash_refresh_token, get_current_user
from pydantic import BaseModel
import uuid
from fastapi.responses import JSONResponse
import datetime
from typing import List
from langchain_groq import ChatGroq
from config.settings import GROQ_API_KEY, IS_DEVELOPMENT
from langchain_core.output_parsers import PydanticOutputParser

class RegisterUser(BaseModel):
    full_name: str
    email: str
    password: str
    position: str
    department: str
    position_level: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PositionSkillsExtraction(BaseModel):
    skills: List[str]

router = APIRouter(tags=["auth"])


def issue_refresh_token(db: Session, user_id: int):
    token_value = str(uuid.uuid4())
    hashed = hash_refresh_token(token_value)
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
    token_db = create_refresh_token(db, user_id, hashed, expires)
    return token_value, token_db

def generate_skills_for_position(position: str, position_level: str) -> list[str]:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY
    )

    prompt = (
        f"Generate a JSON list of hard skills for the position '{position}' at level '{position_level}'. "
        "Include skills from lower levels for senior roles. "
        "Focus ON tools, technologies, programming languages, frameworks, NOT on domain knowledge or soft skills (e.g. google meet is better than video conferencing). "
        "Limit: Intern=5 skills, Junior=7, Middle=10, Senior/Team Lead=15. "
        "Return JSON exactly like this: {\"skills\": [\"skill1\", \"skill2\"]}. "
        "Do NOT include explanations, markdown, or anything else."
    )


    parser = PydanticOutputParser(pydantic_object=PositionSkillsExtraction)

    try:
        response = llm.invoke([{"role": "system", "content": prompt}])
        answer = response.content
        skills = parser.parse(answer).skills
    except Exception as e:
        print(f"LLM parsing failed for {position} {position_level}: {e}")
        skills = []
    return [skill.lower() for skill in skills]


@router.post("/register", response_model=Token)
async def register_user(payload: RegisterUser, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    department = payload.department.upper().strip()
    position = payload.position.upper().strip()
    position_level = payload.position_level.upper().strip()
    password = hash_password(payload.password)
    allowed_departments = {"ML", "DB", "HR", "WEB"}
    allowed_position_levels = {"INTERN", "JUNIOR", "MIDDLE", "SENIOR", "TEAM LEAD"}

    if department not in allowed_departments:
        raise HTTPException(status_code=400, detail="Invalid department")

    if position_level not in allowed_position_levels:
        raise HTTPException(status_code=400, detail="Invalid position level")

    if get_employee_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")

    if (position, position_level) not in get_current_positions_levels(db):
        skills = generate_skills_for_position(position, position_level)
        position_obj = create_position_skill(db, position, position_level, skills)
    else:
        position_obj = get_position_by_name_level(db, position, position_level)

    employee = create_employee(db, payload.full_name, email, password, position_obj.id, department)
    access_token = create_access_token({"sub": employee.email})
    raw_refresh_token, _ = issue_refresh_token(db, employee.id)

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh_token,
        httponly=True,
        secure=not IS_DEVELOPMENT,  # False for HTTP (dev), True for HTTPS (prod)
        samesite="lax" if IS_DEVELOPMENT else "strict",
        max_age=60 * 60 * 24 * 30,
    )
    return response


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    employee = get_employee_by_email(db, form_data.username.lower().strip())
    if not employee or not verify_password(form_data.password, employee.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token({"sub": employee.email})
    raw_refresh_token, _ = issue_refresh_token(db, employee.id)

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh_token,
        httponly=True,
        secure=not IS_DEVELOPMENT,  # False for HTTP (dev), True for HTTPS (prod)
        samesite="lax" if IS_DEVELOPMENT else "strict",
        max_age=60 * 60 * 24 * 30,
    )
    return response


@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    token_cookie = request.cookies.get("refresh_token")
    if not token_cookie:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    hashed_cookie = hash_refresh_token(token_cookie)
    token_db = get_refresh_token(db, hashed_cookie)

    if not token_db:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

    now = datetime.datetime.now(datetime.timezone.utc)
    expires_at = token_db.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)
    if expires_at < now:
        delete_refresh_token(db, hashed_cookie)
        raise HTTPException(status_code=403, detail="Refresh token expired")

    delete_refresh_token(db, hashed_cookie)

    employee = get_user_by_refresh_token(db, token_db)
    access_token = create_access_token({"sub": employee.email})
    raw_refresh_token, _ = issue_refresh_token(db, employee.id)

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh_token,
        httponly=True,
        secure=not IS_DEVELOPMENT,  # False for HTTP (dev), True for HTTPS (prod)
        samesite="lax" if IS_DEVELOPMENT else "strict",
        max_age=60 * 60 * 24 * 30
    )
    return response


@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    token_cookie = request.cookies.get("refresh_token")
    if token_cookie:
        delete_refresh_token(db, hash_refresh_token(token_cookie))

    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("refresh_token")
    return response


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "department": current_user.department,
        "position": current_user.position_obj.position,
        "position_level": current_user.position_obj.position_level
    }