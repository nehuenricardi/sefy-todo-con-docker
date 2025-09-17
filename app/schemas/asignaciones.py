from pydantic import BaseModel
from typing import Optional
from datetime import date

class AsignacionBase(BaseModel):
    id_obra: int
    dni_usuario: str
    rol_empleado: str
    fecha_asignacion: Optional[date] = None  # si no viene, la BD pone CURRENT_DATE
    activo: Optional[bool] = True

class AsignacionCreate(AsignacionBase):
    pass

class AsignacionResponse(AsignacionBase):
    id_asignacion: int

    class Config:
        orm_mode = True
        # Pydantic v2:
        # model_config = {"from_attributes": True}
