from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.obra import Obra
from app.schemas.obra import ObraCreate, ObraResponse

router = APIRouter(prefix="/obras", tags=["obras"])

@router.post("/", response_model=ObraResponse, status_code=201)
def crear_obra(obra: ObraCreate, db: Session = Depends(get_db)):
    nueva_obra = Obra(**obra.dict())
    db.add(nueva_obra)
    db.commit()
    db.refresh(nueva_obra)
    return nueva_obra

@router.get("/hello")
def hello():
    return {"message": "Hola desde el endpoint de obras"}
