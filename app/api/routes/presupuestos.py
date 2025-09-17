from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.presupuesto import Presupuesto
from app.models.obra import Obra
from app.schemas.presupuesto import PresupuestoCreate, PresupuestoResponse

router = APIRouter(prefix="/presupuestos", tags=["presupuestos"])

@router.post("/", response_model=PresupuestoResponse, status_code=201)
def crear_presupuesto(data: PresupuestoCreate, db: Session = Depends(get_db)):
    # Validaciones simples
    if data.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
    # Verificar que exista la obra
    obra = db.get(Obra, data.id_obra)
    if not obra:
        raise HTTPException(status_code=404, detail="La obra indicada no existe")

    nuevo = Presupuesto(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/hello")
def hello():
    return {"message": "Hola desde el endpoint de presupuestos"}
