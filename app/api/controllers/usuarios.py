from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.usuario import User
from app.schemas.usuario import UsuarioCreate

def crear_usuario_controller(usuario_data: UsuarioCreate, db: Session) -> User:
    if db.query(User).filter(User.dni == usuario_data.dni).first():
        raise HTTPException(status_code=400, detail="El DNI ya existe")
    if usuario_data.email and db.query(User).filter(User.email == usuario_data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está en uso")

    nuevo_usuario = User(**usuario_data.dict())
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario
