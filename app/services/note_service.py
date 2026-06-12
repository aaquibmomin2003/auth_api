from sqlalchemy.orm import Session

from ..models import Note


def create_note(
    title: str,
    content: str,
    user_id: int,
    db: Session
):
    note = Note(
        title=title,
        content=content,
        owner_id=user_id
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note

def get_notes(
    user_id: int,
    db: Session
):
    return (
        db.query(Note)
        .filter(
            Note.owner_id == user_id
        )
        .all()
    )
    
def get_note_by_id(
    note_id: int,
    user_id: int,
    db: Session
):
    return (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.owner_id == user_id
        )
        .first()
    )
    
def update_note(
    note_id: int,
    title: str,
    content: str,
    user_id: int,
    db: Session
):
    note = (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.owner_id == user_id
        )
        .first()
    )

    if not note:
        return None

    note.title = title
    note.content = content

    db.commit()
    db.refresh(note)

    return note

def delete_note(
    note_id: int,
    user_id: int,
    db: Session
):
    note = (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.owner_id == user_id
        )
        .first()
    )

    if not note:
        return False

    db.delete(note)
    db.commit()

    return True