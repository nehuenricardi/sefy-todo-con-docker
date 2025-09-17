from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.asignacion import Asignacion
from app.models.obra import Obra
from app.models.usuario import User
from app.schemas.asignacion import AsignacionCreate

def crear_asignacion_controller(data: AsignacionCreate, db: Session) -> Asignacion:
    if not db.get(Obra, data.id_obra):
        raise HTTPException(status_code=404, detail="La obra indicada no existe")
    if not db.get(User, data.dni_usuario):
        raise HTTPException(status_code=404, detail="El usuario indicado no existe")

    nueva = Asignacion(**data.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva
