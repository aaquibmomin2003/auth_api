from sqlalchemy.orm import Session

from ..models import User
from ..auth import (
    hash_password,
    verify_password,
    create_access_token
)
from ..exceptions import (
    BadRequestException,
    UnauthorizedException
)


def register_user(
    email: str,
    password: str,
    db: Session
):
    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise BadRequestException(
            "Email already exists"
        )

    user = User(
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(
    email: str,
    password: str,
    db: Session
):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise UnauthorizedException(
            "Invalid credentials"
        )

    if not verify_password(
        password,
        user.password
    ):
        raise UnauthorizedException(
            "Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": user.email
        }
    )

    return token