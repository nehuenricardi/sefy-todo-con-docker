# app/routes/asignacion.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.asignacion import Asignacion
from app.models.obra import Obra
from app.models.usuario import User
from app.schemas.asignacion import AsignacionCreate, AsignacionResponse

router = APIRouter(prefix="/asignaciones", tags=["asignaciones"])

@router.post("/", response_model=AsignacionResponse, status_code=201)
def crear_asignacion(data: AsignacionCreate, db: Session = Depends(get_db)):
    # Validar existencia de obra y usuario
    if not db.get(Obra, data.id_obra):
        raise HTTPException(status_code=404, detail="La obra indicada no existe")
    if not db.get(User, data.dni_usuario):
        raise HTTPException(status_code=404, detail="El usuario indicado no existe")

    nueva = Asignacion(**data.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/hello")
def hello():
    return {"message": "Hola desde el endpoint de asignaciones"}
