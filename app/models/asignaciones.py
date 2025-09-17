from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Asignacion(Base):
    __tablename__ = "asignaciones"

    id_asignacion = Column(Integer, primary_key=True, index=True)
    id_obra = Column(Integer, ForeignKey("obras.id_obra", ondelete="CASCADE"), nullable=False)
    dni_usuario = Column(String(15), ForeignKey("usuarios.dni", ondelete="CASCADE"), nullable=False)
    rol_empleado = Column(String(100), nullable=False)
    fecha_asignacion = Column(Date, server_default=func.current_date(), nullable=True)
    activo = Column(Boolean, default=True)

    # Relaciones opcionales (útiles para joins, no obligatorias)
    # obra = relationship("Obra", backref="asignaciones")
    # usuario = relationship("User", backref="asignaciones")
