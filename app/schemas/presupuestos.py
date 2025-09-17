from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class PresupuestoBase(BaseModel):
    id_obra: int
    monto: Decimal
    tipo_materiales: Optional[str] = None
    fecha_presupuesto: Optional[date] = None  # si no viene, la BD usa CURRENT_DATE

class PresupuestoCreate(PresupuestoBase):
    pass

class PresupuestoResponse(PresupuestoBase):
    id_presupuesto: int

    class Config:
        orm_mode = True
