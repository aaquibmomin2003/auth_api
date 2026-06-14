from fastapi import FastAPI

from .database import engine
from .database import Base

import app.models

from .routes import router
from fastapi.middleware.cors import CORSMiddleware

from .exceptions import (
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    BadRequestException
)

from .handlers import (
    not_found_handler,
    unauthorized_handler,
    forbidden_handler,
    bad_request_handler
)


app = FastAPI()

app.add_exception_handler(
    NotFoundException,
    not_found_handler
)

app.add_exception_handler(
    UnauthorizedException,
    unauthorized_handler
)

app.add_exception_handler(
    ForbiddenException,
    forbidden_handler
)

app.add_exception_handler(
    BadRequestException,
    bad_request_handler
)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Auth API Running"
    }