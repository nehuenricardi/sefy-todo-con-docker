from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.presupuesto import Presupuesto
from app.models.obra import Obra
from app.schemas.presupuesto import PresupuestoCreate

def crear_presupuesto_controller(data: PresupuestoCreate, db: Session) -> Presupuesto:
    if data.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
    if not db.get(Obra, data.id_obra):
        raise HTTPException(status_code=404, detail="La obra indicada no existe")

    nuevo = Presupuesto(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo
