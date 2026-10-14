from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import bcrypt

from app.database import get_db
import app.models as models
import app.schemas as schemas

router = APIRouter()

def verificar_password(password_plana: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password_plana.encode('utf-8'), password_hash.encode('utf-8'))

@router.post("/auth/registro", response_model=schemas.LoginResponse, tags=["Autenticacion"])
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(models.Usuario.username == usuario.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    hashed = bcrypt.hashpw(usuario.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    nuevo = models.Usuario(
        username=usuario.username, password_hash=hashed,
        nombre_completo=usuario.nombre_completo, rol=usuario.rol
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"username": nuevo.username, "nombre_completo": nuevo.nombre_completo, "rol": nuevo.rol, "mensaje": "Registrado con exito"}

@router.post("/auth/login", response_model=schemas.LoginResponse, tags=["Autenticacion"])
def login(credenciales: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.username == credenciales.username).first()
    if not usuario or not verificar_password(credenciales.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"username": usuario.username, "nombre_completo": usuario.nombre_completo, "rol": usuario.rol, "mensaje": "OK"}

# --- CLIENTES Y VEHICULOS ---
@router.post("/clientes", response_model=schemas.ClienteResponse, tags=["Clientes"])
def crear_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    if db.query(models.Cliente).filter(models.Cliente.documento == cliente.documento).first():
        raise HTTPException(status_code=400, detail="Documento ya registrado")
    nuevo = models.Cliente(**cliente.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/clientes", response_model=List[schemas.ClienteResponse], tags=["Clientes"])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(models.Cliente).all()

@router.post("/vehiculos", response_model=schemas.VehiculoResponse, tags=["Vehiculos"])
def crear_vehiculo(vehiculo: schemas.VehiculoCreate, db: Session = Depends(get_db)):
    if db.query(models.Vehiculo).filter(models.Vehiculo.placa == vehiculo.placa).first():
        raise HTTPException(status_code=400, detail="Placa ya registrada")
    nuevo = models.Vehiculo(**vehiculo.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/vehiculos", response_model=List[schemas.VehiculoResponse], tags=["Vehiculos"])
def listar_vehiculos(db: Session = Depends(get_db)):
    return db.query(models.Vehiculo).all()

# --- ORDENES ---
@router.post("/ordenes", response_model=schemas.OrdenResponse, tags=["Ordenes"])
def crear_orden(orden: schemas.OrdenCreate, db: Session = Depends(get_db)):
    if not db.query(models.Vehiculo).filter(models.Vehiculo.id == orden.vehiculo_id).first():
        raise HTTPException(status_code=404, detail="Vehiculo no existe")
    
    nueva = models.OrdenServicio(
        vehiculo_id=orden.vehiculo_id,
        tipo_servicio=orden.tipo_servicio,
        diagnostico=orden.diagnostico,
        estado=orden.estado,
        costo_total=orden.costo_total
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    log = models.Trazabilidad(
        usuario=orden.nombre_solicitante or "Usuario",
        rol=orden.rol_solicitante or "Cliente",
        servicio=orden.tipo_servicio,
        vehiculo_id=orden.vehiculo_id,
        accion=f"Creacion de ticket #{nueva.id} [{orden.tipo_servicio}]"
    )
    db.add(log)
    db.commit()
    return nueva

@router.get("/ordenes", response_model=List[schemas.OrdenResponse], tags=["Ordenes"])
def listar_ordenes(db: Session = Depends(get_db)):
    return db.query(models.OrdenServicio).order_by(models.OrdenServicio.id.desc()).all()

@router.patch("/ordenes/{orden_id}/operativo", response_model=schemas.OrdenResponse, tags=["Ordenes"])
def actualizar_orden_operativo(orden_id: int, payload: schemas.OrdenUpdateOperativo, db: Session = Depends(get_db)):
    orden = db.query(models.OrdenServicio).filter(models.OrdenServicio.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    estado_ant = orden.estado
    orden.estado = payload.estado
    
    if payload.tecnico_asignado:
        orden.tecnico_asignado = payload.tecnico_asignado
    if payload.checklist_tecnico:
        orden.checklist_tecnico = payload.checklist_tecnico
    if payload.repuestos_usados:
        orden.repuestos_usados = payload.repuestos_usados
    if payload.dictamen_garantia:
        orden.dictamen_garantia = payload.dictamen_garantia
    if payload.costo_total is not None:
        orden.costo_total = payload.costo_total
        
    db.commit()
    db.refresh(orden)

    detalle = f"Transicion: {estado_ant} -> {payload.estado}"
    if payload.observacion:
        detalle += f" | {payload.observacion}"

    log = models.Trazabilidad(
        usuario=payload.nombre_responsable,
        rol=payload.rol_responsable,
        servicio=orden.tipo_servicio,
        vehiculo_id=orden.vehiculo_id,
        accion=detalle
    )
    db.add(log)
    db.commit()
    return orden

# --- CANAL DIRECTO DE NOVEDADES (CHAT / MENSAJES) ---
@router.post("/ordenes/{orden_id}/mensajes", response_model=schemas.MensajeResponse, tags=["Novedades"])
def registrar_mensaje(orden_id: int, msg: schemas.MensajeCreate, db: Session = Depends(get_db)):
    orden = db.query(models.OrdenServicio).filter(models.OrdenServicio.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    nuevo_mensaje = models.MensajeNovedad(
        orden_id=orden_id,
        remitente=msg.remitente,
        rol=msg.rol,
        mensaje=msg.mensaje
    )
    db.add(nuevo_mensaje)
    db.commit()
    db.refresh(nuevo_mensaje)

    # Registrar en auditoría la alerta
    log = models.Trazabilidad(
        usuario=msg.remitente,
        rol=msg.rol,
        servicio=orden.tipo_servicio,
        vehiculo_id=orden.vehiculo_id,
        accion=f"Novedad reportada en Ticket #{orden_id}: {msg.mensaje[:60]}"
    )
    db.add(log)
    db.commit()

    return nuevo_mensaje

@router.get("/ordenes/{orden_id}/mensajes", response_model=List[schemas.MensajeResponse], tags=["Novedades"])
def listar_mensajes_orden(orden_id: int, db: Session = Depends(get_db)):
    return db.query(models.MensajeNovedad).filter(models.MensajeNovedad.orden_id == orden_id).order_by(models.MensajeNovedad.id.asc()).all()

# --- TRAZABILIDAD ---
@router.get("/trazabilidad", response_model=List[schemas.TrazabilidadResponse], tags=["Auditoria"])
def listar_trazabilidad(db: Session = Depends(get_db)):
<<<<<<< HEAD
    return db.query(models.Trazabilidad).order_by(models.Trazabilidad.id.desc()).all()
=======
    return db.query(models.Trazabilidad).order_by(models.Trazabilidad.id.desc()).all()
>>>>>>> be3331f48e28d95f66a3b7a6bfdd7498a5a201ae
