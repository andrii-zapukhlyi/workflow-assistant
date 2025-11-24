from fastapi import FastAPI
from api.qa_router import router as qa_router

def main():
    app = FastAPI()
    app.include_router(qa_router, prefix="/api")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()