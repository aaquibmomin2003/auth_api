from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import (
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    BadRequestException
)


async def not_found_handler(
    request: Request,
    exc: NotFoundException
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.detail
        }
    )


async def unauthorized_handler(
    request: Request,
    exc: UnauthorizedException
):
    return JSONResponse(
        status_code=401,
        content={
            "detail": exc.detail
        }
    )


async def forbidden_handler(
    request: Request,
    exc: ForbiddenException
):
    return JSONResponse(
        status_code=403,
        content={
            "detail": exc.detail
        }
    )
    
async def bad_request_handler(
    request: Request,
    exc: BadRequestException
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.detail
        }
    )