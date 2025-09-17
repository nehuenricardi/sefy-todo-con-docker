from sqlalchemy import Column, Integer, String, Date, text
from app.database.database import Base

class Obra(Base):
    __tablename__ = "obras"

    id_obra = Column(Integer, primary_key=True, index=True)
    nombre_obra = Column(String(150), nullable=False)
    direccion = Column(String(200), nullable=False)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    estado = Column(String(50), server_default=text("'En progreso'"))
