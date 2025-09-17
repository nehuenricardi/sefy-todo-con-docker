from pydantic import BaseModel
from typing import Optional
from datetime import date

class ObraBase(BaseModel):
    nombre_obra: str
    direccion: str
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = "En progreso"

class ObraCreate(ObraBase):
    pass

class ObraResponse(ObraBase):
    id_obra: int

    class Config:
        orm_mode = True
