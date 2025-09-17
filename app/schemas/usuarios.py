from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    es_admin: Optional[bool] = False

class UsuarioCreate(UsuarioBase):
    dni: str

class UsuarioResponse(UsuarioBase):
    dni: str
    fecha_alta: date

    class Config:
        orm_mode = True
