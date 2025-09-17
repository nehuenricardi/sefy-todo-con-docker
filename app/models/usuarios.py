from sqlalchemy import Column, String, Boolean, Date, func
from sqlalchemy.orm import declarative_mixin
from app.database.database import Base

class User(Base):
    __tablename__ = "usuarios"

    dni = Column(String(15), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(20))
    email = Column(String(120), unique=True)
    direccion = Column(String(200))
    fecha_alta = Column(Date, server_default=func.current_date())
    es_admin = Column(Boolean, default=False)
