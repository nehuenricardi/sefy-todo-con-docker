from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime, time
from pydantic import BaseModel

from fastapi.security import OAuth2PasswordRequestForm

from app.database.database import get_db

# Seguridad
from app.security.jwt import create_access_token
from app.security.auth import get_current_user

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
# LOGIN con JWT (usando dni + nombre)
# ---------------------------

class LoginRequest(BaseModel):
    dni: str
    nombre: str

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Recibe: dni y nombre como JSON.
    Devuelve: access_token Bearer JWT.
    """
    user = db.query(User).filter(User.dni == data.dni, User.nombre == data.nombre).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    # El subject del token será el dni
    access_token = create_access_token(data={"sub": user.dni})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=UsuarioResponse)
def me(current_user: User = Depends(get_current_user)):
    """Devuelve el usuario autenticado a partir del token Bearer."""
    return current_user

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

    # Evitar duplicado de email/mail
    # Preferimos 'mail' si tu modelo lo usa (como en auth.py). Si tu schema usa 'email', mapear a 'mail'.
    email_value = getattr(data, "email", None) or getattr(data, "mail", None)
    if email_value and db.query(User).filter(User.mail == email_value).first():
        raise HTTPException(status_code=400, detail="El email ya está en uso")

    # Construcción del modelo
    nuevo = User(**data.dict())

    # Si el schema trae password plano, lo hasheamos y lo guardamos en hashed_password
    if hasattr(data, "password") and getattr(data, "password"):
        hp = hash_password(getattr(data, "password"))
        # asegurar atributo en el modelo
        setattr(nuevo, "hashed_password", hp)

    # Si el schema usa 'email' pero el modelo usa 'mail', mapear:
    if hasattr(nuevo, "email") and hasattr(nuevo, "mail") and nuevo.email and not nuevo.mail:
        nuevo.mail = nuevo.email  # mantener compatibilidad con auth.py

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

    email_value = getattr(data, "email", None) or getattr(data, "mail", None)
    if email_value and email_value != getattr(u, "mail", None):
        if db.query(User).filter(User.mail == email_value).first():
            raise HTTPException(status_code=400, detail="El email ya está en uso")

    # actualizar campos simples
    for k, v in data.dict().items():
        # no pisar hashed_password por error si el schema no lo trae
        if k == "password" and v:
            # si envían password en update, re-hasheamos
            setattr(u, "hashed_password", hash_password(v))
        elif hasattr(u, k):
            setattr(u, k, v)

    # sincronizar email->mail si corresponde
    if hasattr(u, "email") and hasattr(u, "mail") and getattr(u, "email", None):
        u.mail = u.email

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
# ASISTENCIAS (CRUD + Tomar asistencia)
# =====================================================
ESTADOS_VALIDOS = {"Presente", "Ausente", "Justificado"}

class TomarAsistenciaBody(BaseModel):
    dni_usuario: str
    id_asignacion: int
    dia: Optional[date] = None
    estado: Optional[str] = "Presente"
    hora_entrada: Optional[time] = None
    hora_salida: Optional[time] = None

def _validar_fk_asistencia(db: Session, dni_usuario: str, id_asignacion: int):
    if not db.get(User, dni_usuario):
        raise HTTPException(status_code=404, detail="El usuario (dni) no existe")
    asign = db.get(Asignacion, id_asignacion)
    if not asign:
        raise HTTPException(status_code=404, detail="La asignación no existe")
    if asign.dni_usuario != dni_usuario:
        raise HTTPException(status_code=400, detail="La asignación no corresponde al usuario")

@app.post("/asistencias/", response_model=AsistenciaResponse, status_code=201)
def crear_asistencia(data: AsistenciaCreate, db: Session = Depends(get_db)):
    _validar_fk_asistencia(db, data.dni_usuario, data.id_asignacion)
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
    _validar_fk_asistencia(db, data.dni_usuario, data.id_asignacion)
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

@app.post("/asistencias/tomar", response_model=AsistenciaResponse, status_code=200)
def tomar_asistencia(body: TomarAsistenciaBody, db: Session = Depends(get_db)):
    dia = body.dia or date.today()
    estado = body.estado or "Presente"
    _validar_fk_asistencia(db, body.dni_usuario, body.id_asignacion)
    if estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Estado inválido")
    existente = (
        db.query(Asistencia)
        .filter(
            Asistencia.dni_usuario == body.dni_usuario,
            Asistencia.id_asignacion == body.id_asignacion,
            Asistencia.dia == dia
        )
        .first()
    )
    if existente:
        existente.estado = estado
        if body.hora_entrada is not None:
            existente.hora_entrada = body.hora_entrada
        if body.hora_salida is not None:
            existente.hora_salida = body.hora_salida
        db.commit()
        db.refresh(existente)
        return existente
    else:
        nueva = Asistencia(
            dni_usuario=body.dni_usuario,
            id_asignacion=body.id_asignacion,
            dia=dia,
            estado=estado,
            hora_entrada=body.hora_entrada,
            hora_salida=body.hora_salida,
        )
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva

@app.post("/asistencias/{id_asignacion}/{dni}/entrada", response_model=AsistenciaResponse)
def marcar_entrada(id_asignacion: int, dni: str, db: Session = Depends(get_db)):
    _validar_fk_asistencia(db, dni, id_asignacion)
    hoy = date.today()
    ahora = datetime.now().time()
    a = (
        db.query(Asistencia)
        .filter(
            Asistencia.dni_usuario == dni,
            Asistencia.id_asignacion == id_asignacion,
            Asistencia.dia == hoy
        )
        .first()
    )
    if a:
        a.estado = "Presente"
        a.hora_entrada = ahora
    else:
        a = Asistencia(
            dni_usuario=dni,
            id_asignacion=id_asignacion,
            dia=hoy,
            estado="Presente",
            hora_entrada=ahora
        )
        db.add(a)
    db.commit()
    db.refresh(a)
    return a

@app.post("/asistencias/{id_asignacion}/{dni}/salida", response_model=AsistenciaResponse)
def marcar_salida(id_asignacion: int, dni: str, db: Session = Depends(get_db)):
    _validar_fk_asistencia(db, dni, id_asignacion)
    hoy = date.today()
    ahora = datetime.now().time()
    a = (
        db.query(Asistencia)
        .filter(
            Asistencia.dni_usuario == dni,
            Asistencia.id_asignacion == id_asignacion,
            Asistencia.dia == hoy
        )
        .first()
    )
    if not a:
        a = Asistencia(
            dni_usuario=dni,
            id_asignacion=id_asignacion,
            dia=hoy,
            estado="Presente",
            hora_entrada=ahora,
            hora_salida=ahora
        )
        db.add(a)
    else:
        a.hora_salida = ahora
    db.commit()
    db.refresh(a)
    return a

# ---------------------------
# EJECUCIÓN LOCAL (DEV)
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
