from fastapi import FastAPI
from backend.api.qa_router import router as qa_router
from backend.db.db_auth import get_db
from backend.db.crud import clear_chat_history, clear_chat_sessions

def main():
    # db = next(get_db())
    # clear_chat_history(db)
    # clear_chat_sessions(db)

    app = FastAPI()
    app.include_router(qa_router, prefix="/api")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()