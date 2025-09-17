from sqlalchemy.orm import Session
from app.models.obra import Obra
from app.schemas.obra import ObraCreate

def crear_obra_controller(obra_data: ObraCreate, db: Session) -> Obra:
    nueva_obra = Obra(**obra_data.dict())
    db.add(nueva_obra)
    db.commit()
    db.refresh(nueva_obra)
    return nueva_obra
