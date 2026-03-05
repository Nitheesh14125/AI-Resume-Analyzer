from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import public_router, router as resume_router
from app.database.db_connection import engine
from app.models import database_models

database_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router)
app.include_router(public_router)

@app.get("/")
def home():
    return {"message": "AI Resume Analyzer Backend Running"}
