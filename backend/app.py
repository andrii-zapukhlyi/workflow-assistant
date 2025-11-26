from fastapi import FastAPI
from backend.api import auth_router, chat_router

def main():
    app = FastAPI()
    app.include_router(auth_router.router, prefix="/auth")
    app.include_router(chat_router.router, prefix="/chat")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()