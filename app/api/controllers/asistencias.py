from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.asistencia import Asistencia
from app.models.usuario import User
from app.models.asignacion import Asignacion
from app.schemas.asistencia import AsistenciaCreate

ESTADOS_VALIDOS = {"Presente", "Ausente", "Justificado"}

def crear_asistencia_controller(data: AsistenciaCreate, db: Session) -> Asistencia:
    if not db.get(User, data.dni_usuario):
        raise HTTPException(status_code=404, detail="El usuario (dni) no existe")
    if not db.get(Asignacion, data.id_asignacion):
        raise HTTPException(status_code=404, detail="La asignación no existe")
    if data.estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Estado inválido")

    nuevo = Asistencia(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo
