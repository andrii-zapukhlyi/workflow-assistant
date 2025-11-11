from db.crud import get_employee_by_email
from db.db_auth import SessionLocal

db = SessionLocal()

email = input("Enter your email to show an available documentation: ")

try:
    employee = get_employee_by_email(db, email)
except ValueError as e:
    print(e)
    exit(1)