from db.crud import get_employee_by_email
from db.db_auth import SessionLocal
from rag.retriever import retrieve_similar_documents

def main():

    db = SessionLocal()
    email = input("Enter employee email: ")
    query = input("Enter your query: ")
    employee = get_employee_by_email(db, email)
    docs = retrieve_similar_documents(query, space_key=employee.department, k=2)

if __name__ == "__main__":
    main()