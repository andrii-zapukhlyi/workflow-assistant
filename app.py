from db.crud import get_employee_by_email, clear_chat_history, clear_chat_sessions
from db.db_auth import SessionLocal
from agents.qa_agent import handle_user_query

def main():
    db = SessionLocal()
    email = input("Enter employee email: ")
    query = input("Enter your query: ")
    employee = get_employee_by_email(db, email)

    answer, links = handle_user_query(employee.id, query, employee.department, db)

    print("\nAnswer:")
    print(answer)
    print("\nSource Links:")
    print(links)

    clear_db = input("Clear all chat sessions and chats? (y/n): ")
    if clear_db.lower() == 'y':
        clear_chat_sessions(db)
        clear_chat_history(db)

if __name__ == "__main__":
    main()