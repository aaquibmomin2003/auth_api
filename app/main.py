from fastapi import FastAPI

from .database import engine
from .database import Base

import app.models

from .routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)

@app.get("/")
def home():
    return {
        "message": "Auth API Running"
    }