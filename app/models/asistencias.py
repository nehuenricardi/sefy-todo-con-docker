from sqlalchemy import (
    Column, Integer, String, Date, Time, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.database.database import Base

class Asistencia(Base):
    __tablename__ = "asistencias"

    id_asistencia = Column(Integer, primary_key=True, index=True)
    dni_usuario = Column(String(15), ForeignKey("usuarios.dni", ondelete="CASCADE"), nullable=False)
    id_asignacion = Column(Integer, ForeignKey("asignaciones.id_asignacion", ondelete="CASCADE"), nullable=False)
    dia = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)
    hora_entrada = Column(Time, nullable=True)
    hora_salida = Column(Time, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "estado IN ('Presente','Ausente','Justificado')",
            name="chk_asistencias_estado"
        ),
    )

    # Relaciones opcionales (útiles para joins)
    # usuario = relationship("User", backref="asistencias")
    # asignacion = relationship("Asignacion", backref="asistencias")
