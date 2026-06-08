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