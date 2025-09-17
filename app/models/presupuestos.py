from sqlalchemy import Column, Integer, Numeric, Text, Date, ForeignKey, func
from app.database.database import Base

class Presupuesto(Base):
    __tablename__ = "presupuestos"

    id_presupuesto = Column(Integer, primary_key=True, index=True)
    id_obra = Column(Integer, ForeignKey("obras.id_obra", ondelete="CASCADE"), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    tipo_materiales = Column(Text, nullable=True)
    fecha_presupuesto = Column(Date, server_default=func.current_date(), nullable=True)
