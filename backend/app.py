from fastapi import FastAPI
from backend.api import auth_router, chat_router
from fastapi.middleware.cors import CORSMiddleware

def main():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router.router, prefix="/auth")
    app.include_router(chat_router.router, prefix="/chat")

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()