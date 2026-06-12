from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RoleUpdate(BaseModel):
    role: str


class NoteCreate(BaseModel):
    title: str
    content: str


# --------------------
# RESPONSE SCHEMAS
# --------------------

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True
        
class OwnerResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class NoteWithOwnerResponse(BaseModel):
    id: int
    title: str
    content: str

    owner: OwnerResponse

    class Config:
        from_attributes = True