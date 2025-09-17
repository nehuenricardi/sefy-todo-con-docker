from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class AsistenciaBase(BaseModel):
    dni_usuario: str
    id_asignacion: int
    dia: date
    estado: str  # 'Presente' | 'Ausente' | 'Justificado'
    hora_entrada: Optional[time] = None
    hora_salida: Optional[time] = None

class AsistenciaCreate(AsistenciaBase):
    pass

class AsistenciaResponse(AsistenciaBase):
    id_asistencia: int

    class Config:
        orm_mode = True
        # Pydantic v2:
        # model_config = {"from_attributes": True}
