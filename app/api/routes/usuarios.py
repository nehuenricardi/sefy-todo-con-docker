from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.usuario import User
from app.schemas.usuario import UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Evitar duplicados por PK (dni) o email
    if db.query(User).filter(User.dni == usuario.dni).first():
        raise HTTPException(status_code=400, detail="El DNI ya existe")
    if usuario.email and db.query(User).filter(User.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="El email ya está en uso")

    nuevo_usuario = User(**usuario.dict())
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.get("/hello")
def hello():
    return {"message": "Hola desde el endpoint de usuarios"}
