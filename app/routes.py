from .services.note_service import (
    create_note as create_note_service,
        get_notes as get_notes_service,
        get_note_by_id as get_note_by_id_service,
        update_note as update_note_service,
        delete_note as delete_note_service
)
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi import Query
from typing import Literal
from .database import get_db
from .models import User , Note
from .schemas import (
    UserCreate,
    UserLogin,
    RoleUpdate,
    NoteCreate,
    UserResponse,
    NoteResponse,
    OwnerResponse,
    NoteWithOwnerResponse
)
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
    
)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    return user

def get_current_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user
@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        form_data.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        {
            "sub": db_user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
    
@router.get(
    "/admin/users",
    response_model=list[UserResponse]
)
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = None,
    role: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(User)

    # Search by email
    if search:
        query = query.filter(
            User.email.ilike(f"%{search}%")
        )

    # Filter by role
    if role:
        query = query.filter(
            User.role == role
        )

    # Sorting column
    if sort_by == "email":
        sort_column = User.email
    else:
        sort_column = User.id

    # Sorting order
    if order == "desc":
        query = query.order_by(
            sort_column.desc()
        )
    else:
        query = query.order_by(
            sort_column.asc()
        )

    # Pagination
    users = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return users
@router.get(
    "/admin/users/{user_id}",
    response_model=UserResponse
)
def get_user_by_id(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user
@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id:int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id ==user_id)
        .first()
    )
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {
        "message": "User deleted successfully"
    }
@router.put("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role_data: RoleUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if role_data.role not in ["admin", "user"]:
        raise HTTPException(
            status_code=400,
            detail="Role must be admin or user"
        )

    user.role = role_data.role

    db.commit()
    db.refresh(user)

    return {
        "message": "Role updated successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }

@router.get(
    "/notes",
    response_model=list[NoteResponse]
)
def get_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_notes_service(
        user_id=current_user.id,
        db=db
    )
@router.post("/notes")
def create_note(
    note: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_note = create_note_service(
        title=note.title,
        content=note.content,
        user_id=current_user.id,
        db=db
    )

    return {
        "message": "Note created successfully",
        "note": {
            "id": new_note.id,
            "title": new_note.title,
            "content": new_note.content,
            "owner_id": new_note.owner_id
        }
    }

@router.get(
    "/notes/{note_id}",
    response_model=NoteResponse
)
def get_note_by_id(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = get_note_by_id_service(
        note_id=note_id,
        user_id=current_user.id,
        db=db
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note
@router.get(
    "/notes/{note_id}/details",
    response_model=NoteWithOwnerResponse
)
def get_note_details(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.owner_id == current_user.id
        )
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note
@router.put("/notes/{note_id}")
def update_note(
    note_id: int,
    note: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_note = update_note_service(
        note_id=note_id,
        title=note.title,
        content=note.content,
        user_id=current_user.id,
        db=db
    )

    if not updated_note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return {
        "message": "Note updated successfully"
    }
@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deleted = delete_note_service(
        note_id=note_id,
        user_id=current_user.id,
        db=db
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return {
        "message": "Note deleted successfully"
    }
    