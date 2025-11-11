from db.crud import get_employee_by_email
from db.db_auth import SessionLocal
from rag.confluence_loader import get_available_pages
from rag.embedder import chunk_and_embed_documents

db = SessionLocal()

email = input("Enter your email to show an available documentation: ")

try:
    employee = get_employee_by_email(db, email)
except ValueError as e:
    print(e)
    exit(1)

docs = get_available_pages(space_key=employee.department)
embedded_docs = chunk_and_embed_documents(docs)
print(embedded_docs)