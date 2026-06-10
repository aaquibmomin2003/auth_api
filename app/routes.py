from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User , Note
from .schemas import (
    UserCreate,
    UserLogin,
    RoleUpdate,
    NoteCreate,
    UserResponse,
    NoteResponse
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
    
@router.get("/admin/users")
def get_all_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]
    
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
    
@router.post("/notes")
def create_note(
    note : NoteCreate,
    current_user : User = Depends(get_current_user),
    db : Session = Depends(get_db)
    
):
    new_note = Note(
        title = note.title,
        content=note.content,
        owner_id = current_user.id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return {
        "message" : "Note created successfully",
        "note":{
            "id": new_note.id,
            "title": new_note.title,
            "content": new_note.content,
            "owner_id": new_note.owner_id
        }
    }
    
@router.get(
    "/notes",
    response_model=list[NoteResponse]
)
def get_my_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notes = (
        db.query(Note)
        .filter(
            Note.owner_id == current_user.id
        )
        .all()
    )

    return notes
    
@router.put("/notes/{note_id}")
def update_note(
    note_id: int,
    note: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_note = (
        db.query(Note)
        .filter(Note.id == note_id)
        .first()
    )

    if not db_note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    if db_note.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed"
        )

    db_note.title = note.title
    db_note.content = note.content

    db.commit()
    db.refresh(db_note)

    return {
        "message": "Note updated successfully"
    }
@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_note = (
        db.query(Note)
        .filter(Note.id == note_id)
        .first()
    )

    if not db_note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    if db_note.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed"
        )

    db.delete(db_note)
    db.commit()

    return {
        "message": "Note deleted successfully"
    }