from sqlalchemy.orm import Session

from ..models import User

def get_users(
    skip: int,
    limit: int,
    search: str | None,
    role: str | None,
    sort_by: str,
    order: str,
    db: Session
):
    query = db.query(User)

    if search:
        query = query.filter(
            User.email.ilike(f"%{search}%")
        )

    if role:
        query = query.filter(
            User.role == role
        )

    if sort_by == "email":
        sort_column = User.email
    else:
        sort_column = User.id

    if order == "desc":
        query = query.order_by(
            sort_column.desc()
        )
    else:
        query = query.order_by(
            sort_column.asc()
        )

    return (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )
    
def get_user_by_id(
    user_id: int,
    db: Session
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )
    
def delete_user(
    user_id: int,
    db: Session
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        return False

    db.delete(user)
    db.commit()

    return True

def update_user_role(
    user_id: int,
    role: str,
    db: Session
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        return None

    user.role = role

    db.commit()
    db.refresh(user)

    return user