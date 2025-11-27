from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.db.db_auth import get_db
from backend.db.crud import get_employee_by_email, create_employee, create_refresh_token, get_refresh_token, get_user_by_refresh_token, delete_refresh_token
from backend.auth.auth import verify_password, create_access_token, hash_password, hash_refresh_token
from pydantic import BaseModel
import uuid
from fastapi.responses import JSONResponse
import datetime

class RegisterUser(BaseModel):
    full_name: str
    email: str
    password: str
    position: str
    department: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


router = APIRouter(tags=["auth"])


def issue_refresh_token(db: Session, user_id: int):
    token_value = str(uuid.uuid4())
    hashed = hash_refresh_token(token_value)
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
    token_db = create_refresh_token(db, user_id, hashed, expires)
    return token_db


@router.post("/register", response_model=Token)
def register_user(payload: RegisterUser, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    department = payload.department.upper().strip()
    position = payload.position.upper().strip()
    password = hash_password(payload.password)
    allowed_departments = {"ML", "DB", "HR", "WEB"}

    if department not in allowed_departments:
        raise HTTPException(status_code=400, detail="Invalid department")

    if get_employee_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")

    employee = create_employee(db, payload.full_name, email, password, position, department)
    access_token = create_access_token({"sub": employee.email})
    refresh_token_db = issue_refresh_token(db, employee.id)

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_db.token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 30,
    )
    return response


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    employee = get_employee_by_email(db, form_data.username.lower().strip())
    if not employee or not verify_password(form_data.password, employee.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token({"sub": employee.email})
    refresh_token_db = issue_refresh_token(db, employee.id)

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_db.token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 30,
    )
    return response


@router.post("/refresh", response_model=Token)
def refresh_token(request: Request, db: Session = Depends(get_db)):
    token_cookie = request.cookies.get("refresh_token")
    if not token_cookie:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    hashed_cookie = hash_refresh_token(token_cookie)
    token_db = get_refresh_token(db, hashed_cookie)

    if not token_db:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

    now = datetime.datetime.now(datetime.timezone.utc)
    if token_db.expires_at < now:
        delete_refresh_token(db, hashed_cookie)
        raise HTTPException(status_code=403, detail="Refresh token expired")

    delete_refresh_token(db, hashed_cookie)

    employee = get_user_by_refresh_token(db, token_db)
    access_token = create_access_token({"sub": employee.email})
    refresh_db = issue_refresh_token(db, employee.id)

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=refresh_db.token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 30
    )
    return response


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    token_cookie = request.cookies.get("refresh_token")
    if token_cookie:
        delete_refresh_token(db, hash_refresh_token(token_cookie))

    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("refresh_token")
    return response