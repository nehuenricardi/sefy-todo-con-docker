from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.asistencia import Asistencia
from app.models.usuario import User
from app.models.asignacion import Asignacion
from app.schemas.asistencia import AsistenciaCreate, AsistenciaResponse

router = APIRouter(prefix="/asistencias", tags=["asistencias"])

ESTADOS_VALIDOS = {"Presente", "Ausente", "Justificado"}

@router.post("/", response_model=AsistenciaResponse, status_code=201)
def crear_asistencia(data: AsistenciaCreate, db: Session = Depends(get_db)):
    # Validaciones de FK
    if not db.get(User, data.dni_usuario):
        raise HTTPException(status_code=404, detail="El usuario (dni) no existe")
    if not db.get(Asignacion, data.id_asignacion):
        raise HTTPException(status_code=404, detail="La asignación no existe")

    # Validar estado permitido
    if data.estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Estado inválido")

    nuevo = Asistencia(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/hello")
def hello():
    return {"message": "Hola desde el endpoint de asistencias"}
