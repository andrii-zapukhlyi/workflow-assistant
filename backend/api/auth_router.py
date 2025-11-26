from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.db.db_auth import get_db
from backend.db.crud import get_employee_by_email, create_employee
from backend.auth.auth import verify_password, create_access_token, hash_password
from pydantic import BaseModel

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

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterUser, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    department = payload.department.upper().strip()
    position = payload.position.upper().strip()
    password = hash_password(payload.password)
    allowed_departments = {"ML", "DB", "HR", "WEB"}

    if department not in allowed_departments:
        raise HTTPException(status_code=400, detail="Invalid department")

    existing = get_employee_by_email(db, email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_employee = create_employee(db, payload.full_name, email, password, position, department)

    token = create_access_token({"sub": new_employee.email})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_employee_by_email(db, form_data.username.lower().strip())
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

