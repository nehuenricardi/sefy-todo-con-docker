# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.database import get_db

# Modelos SQLAlchemy (módulos en PLURAL)
from app.models.usuarios import User
from app.models.obras import Obra
from app.models.presupuestos import Presupuesto
from app.models.asignaciones import Asignacion
from app.models.asistencias import Asistencia

# Schemas Pydantic (módulos en PLURAL)
from app.schemas.usuarios import UsuarioCreate, UsuarioResponse
from app.schemas.obras import ObraCreate, ObraResponse
from app.schemas.presupuestos import PresupuestoCreate, PresupuestoResponse
from app.schemas.asignaciones import AsignacionCreate, AsignacionResponse
from app.schemas.asistencias import AsistenciaCreate, AsistenciaResponse

# ---------------------------
# CREACIÓN DE LA APLICACIÓN
# ---------------------------
app = FastAPI(
    title="Sistema de Obras SEFY",
    description="API para gestionar usuarios, obras, presupuestos, asignaciones y asistencias",
    version="1.0.0",
)

# ---------------------------
# RUTA DE BIENVENIDA
# ---------------------------
@app.get("/")
async def root():
    return {"message": "¡Bienvenido al Sistema de Obras SEFY!"}

# ---------------------------
# HEALTH CHECK
# ---------------------------
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# =====================================================
# USUARIOS (dni PK)
# =====================================================
@app.post("/usuarios/", response_model=UsuarioResponse, status_code=201)
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    if db.get(User, data.dni):
        raise HTTPException(status_code=400, detail="El DNI ya existe")
    if data.email and db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está en uso")

    nuevo = User(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.get("/usuarios/", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/usuarios/{dni}", response_model=UsuarioResponse)
def obtener_usuario(dni: str, db: Session = Depends(get_db)):
    u = db.get(User, dni)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u

@app.put("/usuarios/{dni}", response_model=UsuarioResponse)
def actualizar_usuario(dni: str, data: UsuarioCreate, db: Session = Depends(get_db)):
    u = db.get(User, dni)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if data.email and data.email != u.email:
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="El email ya está en uso")

    for k, v in data.dict().items():
        setattr(u, k, v)

    db.commit()
    db.refresh(u)
    return u

@app.delete("/usuarios/{dni}")
def eliminar_usuario(dni: str, db: Session = Depends(get_db)):
    u = db.get(User, dni)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(u)
    db.commit()
    return {"message": "Usuario eliminado correctamente"}

# =====================================================
# OBRAS
# =====================================================
@app.post("/obras/", response_model=ObraResponse, status_code=201)
def crear_obra(data: ObraCreate, db: Session = Depends(get_db)):
    nueva = Obra(**data.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.get("/obras/", response_model=List[ObraResponse])
def listar_obras(db: Session = Depends(get_db)):
    return db.query(Obra).all()

@app.get("/obras/{id_obra}", response_model=ObraResponse)
def obtener_obra(id_obra: int, db: Session = Depends(get_db)):
    o = db.get(Obra, id_obra)
    if not o:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    return o

@app.put("/obras/{id_obra}", response_model=ObraResponse)
def actualizar_obra(id_obra: int, data: ObraCreate, db: Session = Depends(get_db)):
    o = db.get(Obra, id_obra)
    if not o:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    for k, v in data.dict().items():
        setattr(o, k, v)
    db.commit()
    db.refresh(o)
    return o

@app.delete("/obras/{id_obra}")
def eliminar_obra(id_obra: int, db: Session = Depends(get_db)):
    o = db.get(Obra, id_obra)
    if not o:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    db.delete(o)
    db.commit()
    return {"message": "Obra eliminada correctamente"}

# =====================================================
# PRESUPUESTOS
# =====================================================
@app.post("/presupuestos/", response_model=PresupuestoResponse, status_code=201)
def crear_presupuesto(data: PresupuestoCreate, db: Session = Depends(get_db)):
    if data.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
    if not db.get(Obra, data.id_obra):
        raise HTTPException(status_code=404, detail="La obra indicada no existe")

    nuevo = Presupuesto(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.get("/presupuestos/", response_model=List[PresupuestoResponse])
def listar_presupuestos(db: Session = Depends(get_db)):
    return db.query(Presupuesto).all()

@app.get("/presupuestos/{id_presupuesto}", response_model=PresupuestoResponse)
def obtener_presupuesto(id_presupuesto: int, db: Session = Depends(get_db)):
    p = db.get(Presupuesto, id_presupuesto)
    if not p:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return p

@app.put("/presupuestos/{id_presupuesto}", response_model=PresupuestoResponse)
def actualizar_presupuesto(id_presupuesto: int, data: PresupuestoCreate, db: Session = Depends(get_db)):
    p = db.get(Presupuesto, id_presupuesto)
    if not p:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    if data.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
    if not db.get(Obra, data.id_obra):
        raise HTTPException(status_code=404, detail="La obra indicada no existe")

    for k, v in data.dict().items():
        setattr(p, k, v)

    db.commit()
    db.refresh(p)
    return p

@app.delete("/presupuestos/{id_presupuesto}")
def eliminar_presupuesto(id_presupuesto: int, db: Session = Depends(get_db)):
    p = db.get(Presupuesto, id_presupuesto)
    if not p:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    db.delete(p)
    db.commit()
    return {"message": "Presupuesto eliminado correctamente"}

# =====================================================
# ASIGNACIONES
# =====================================================
@app.post("/asignaciones/", response_model=AsignacionResponse, status_code=201)
def crear_asignacion(data: AsignacionCreate, db: Session = Depends(get_db)):
    if not db.get(Obra, data.id_obra):
        raise HTTPException(status_code=404, detail="La obra indicada no existe")
    if not db.get(User, data.dni_usuario):
        raise HTTPException(status_code=404, detail="El usuario indicado no existe")

    nueva = Asignacion(**data.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.get("/asignaciones/", response_model=List[AsignacionResponse])
def listar_asignaciones(db: Session = Depends(get_db)):
    return db.query(Asignacion).all()

@app.get("/asignaciones/{id_asignacion}", response_model=AsignacionResponse)
def obtener_asignacion(id_asignacion: int, db: Session = Depends(get_db)):
    a = db.get(Asignacion, id_asignacion)
    if not a:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return a

@app.put("/asignaciones/{id_asignacion}", response_model=AsignacionResponse)
def actualizar_asignacion(id_asignacion: int, data: AsignacionCreate, db: Session = Depends(get_db)):
    a = db.get(Asignacion, id_asignacion)
    if not a:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    if not db.get(Obra, data.id_obra):
        raise HTTPException(status_code=404, detail="La obra indicada no existe")
    if not db.get(User, data.dni_usuario):
        raise HTTPException(status_code=404, detail="El usuario indicado no existe")

    for k, v in data.dict().items():
        setattr(a, k, v)

    db.commit()
    db.refresh(a)
    return a

@app.delete("/asignaciones/{id_asignacion}")
def eliminar_asignacion(id_asignacion: int, db: Session = Depends(get_db)):
    a = db.get(Asignacion, id_asignacion)
    if not a:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    db.delete(a)
    db.commit()
    return {"message": "Asignación eliminada correctamente"}

# =====================================================
# ASISTENCIAS
# =====================================================
ESTADOS_VALIDOS = {"Presente", "Ausente", "Justificado"}

@app.post("/asistencias/", response_model=AsistenciaResponse, status_code=201)
def crear_asistencia(data: AsistenciaCreate, db: Session = Depends(get_db)):
    if not db.get(User, data.dni_usuario):
        raise HTTPException(status_code=404, detail="El usuario (dni) no existe")
    if not db.get(Asignacion, data.id_asignacion):
        raise HTTPException(status_code=404, detail="La asignación no existe")
    if data.estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Estado inválido")

    nuevo = Asistencia(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.get("/asistencias/", response_model=List[AsistenciaResponse])
def listar_asistencias(db: Session = Depends(get_db)):
    return db.query(Asistencia).all()

@app.get("/asistencias/{id_asistencia}", response_model=AsistenciaResponse)
def obtener_asistencia(id_asistencia: int, db: Session = Depends(get_db)):
    a = db.get(Asistencia, id_asistencia)
    if not a:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    return a

@app.put("/asistencias/{id_asistencia}", response_model=AsistenciaResponse)
def actualizar_asistencia(id_asistencia: int, data: AsistenciaCreate, db: Session = Depends(get_db)):
    a = db.get(Asistencia, id_asistencia)
    if not a:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")

    if not db.get(User, data.dni_usuario):
        raise HTTPException(status_code=404, detail="El usuario (dni) no existe")
    if not db.get(Asignacion, data.id_asignacion):
        raise HTTPException(status_code=404, detail="La asignación no existe")
    if data.estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Estado inválido")

    for k, v in data.dict().items():
        setattr(a, k, v)

    db.commit()
    db.refresh(a)
    return a

@app.delete("/asistencias/{id_asistencia}")
def eliminar_asistencia(id_asistencia: int, db: Session = Depends(get_db)):
    a = db.get(Asistencia, id_asistencia)
    if not a:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    db.delete(a)
    db.commit()
    return {"message": "Asistencia eliminada correctamente"}

# ---------------------------
# EJECUCIÓN LOCAL (DEV)
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

