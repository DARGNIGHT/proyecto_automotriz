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
        raise HTTPException(status_code=400, detail="Documento ya registrado (Control de duplicados)")
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
    placa_limpia = vehiculo.placa.strip().upper()
    if db.query(models.Vehiculo).filter(models.Vehiculo.placa == placa_limpia).first():
        raise HTTPException(status_code=400, detail="Placa ya registrada (Control de duplicados)")
    datos = vehiculo.dict()
    datos["placa"] = placa_limpia
    nuevo = models.Vehiculo(**datos)
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
        accion=f"Creacion de orden Cero Papel #{nueva.id} [{orden.tipo_servicio}]"
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
    
    # BLOQUEO DE SEGURIDAD MECANICLARO: Impedir alteracion de costos sin aprobacion previa del cliente
    if payload.costo_total is not None and float(payload.costo_total) != float(orden.costo_total or 0):
        cot_aprobada = db.query(models.CotizacionRepuesto).filter(
            models.CotizacionRepuesto.orden_id == orden_id,
            models.CotizacionRepuesto.aprobada_cliente == True
        ).first()
        if not cot_aprobada:
            raise HTTPException(
                status_code=403,
                detail="Bloqueo MecaniClaro: No se puede alterar el costo ni liquidar sin aprobacion previa de una cotizacion por parte del conductor."
            )
        total_autorizado = float(cot_aprobada.precio) + float(cot_aprobada.mano_obra)
        if abs(float(payload.costo_total) - total_autorizado) > 1:
            raise HTTPException(
                status_code=403,
                detail=f"Bloqueo MecaniClaro: El valor (${payload.costo_total:,.0f}) difiere del presupuesto autorizado por el conductor (${total_autorizado:,.0f})."
            )

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

# --- COMPARATIVA DE 3 COTIZACIONES Y APROBACION DEL CONDUCTOR ---
@router.post("/ordenes/{orden_id}/cotizaciones", response_model=schemas.CotizacionResponse, tags=["Cotizaciones"])
def agregar_cotizacion(orden_id: int, cot: schemas.CotizacionCreate, db: Session = Depends(get_db)):
    orden = db.query(models.OrdenServicio).filter(models.OrdenServicio.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    # Impedir alteraciones si el cliente ya aprobó una cotización
    ya_aprobada = db.query(models.CotizacionRepuesto).filter(
        models.CotizacionRepuesto.orden_id == orden_id,
        models.CotizacionRepuesto.aprobada_cliente == True
    ).first()
    if ya_aprobada or orden.estado in ["Aprobado por Cliente", "Liquidado y Cerrado"]:
        raise HTTPException(
            status_code=403,
            detail="La orden ya cuenta con una cotizacion aprobada por el conductor; no se permiten alteraciones sin autorizacion."
        )

    # Control de duplicados: mismo proveedor y repuesto en la misma orden
    duplicada = db.query(models.CotizacionRepuesto).filter(
        models.CotizacionRepuesto.orden_id == orden_id,
        models.CotizacionRepuesto.proveedor == cot.proveedor.strip(),
        models.CotizacionRepuesto.nombre_repuesto == cot.nombre_repuesto.strip()
    ).first()
    if duplicada:
        raise HTTPException(
            status_code=400,
            detail="Control de duplicados: Ya registraste este proveedor para ese repuesto en esta orden."
        )

    nueva_cot = models.CotizacionRepuesto(
        orden_id=orden_id,
        proveedor=cot.proveedor.strip(),
        nombre_repuesto=cot.nombre_repuesto.strip(),
        marca=cot.marca.strip(),
        precio=cot.precio,
        mano_obra=cot.mano_obra or 0.0
    )
    db.add(nueva_cot)
    orden.estado = "Esperando Aprobación Cliente"
    db.commit()
    db.refresh(nueva_cot)

    total_cot = float(cot.precio) + float(cot.mano_obra or 0)
    log = models.Trazabilidad(
        usuario=cot.usuario_responsable or "Asesor",
        rol="Asesor",
        servicio=orden.tipo_servicio,
        vehiculo_id=orden.vehiculo_id,
        accion=f"Cotizacion registrada Ticket #{orden_id}: Proveedor {cot.proveedor} ({cot.nombre_repuesto} - {cot.marca}) Total ${total_cot:,.0f}"
    )
    db.add(log)
    db.commit()
    return nueva_cot

@router.get("/ordenes/{orden_id}/cotizaciones", response_model=List[schemas.CotizacionResponse], tags=["Cotizaciones"])
def listar_cotizaciones_orden(orden_id: int, db: Session = Depends(get_db)):
    return db.query(models.CotizacionRepuesto).filter(models.CotizacionRepuesto.orden_id == orden_id).order_by(models.CotizacionRepuesto.precio.asc()).all()

@router.post("/ordenes/{orden_id}/cotizaciones/{cotizacion_id}/aprobar", response_model=schemas.OrdenResponse, tags=["Cotizaciones"])
def aprobar_cotizacion_cliente(orden_id: int, cotizacion_id: int, req: schemas.AprobacionClienteRequest, db: Session = Depends(get_db)):
    orden = db.query(models.OrdenServicio).filter(models.OrdenServicio.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    cot = db.query(models.CotizacionRepuesto).filter(
        models.CotizacionRepuesto.id == cotizacion_id,
        models.CotizacionRepuesto.orden_id == orden_id
    ).first()
    if not cot:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")

    # Desmarcar otras y aprobar la elegida
    todas = db.query(models.CotizacionRepuesto).filter(models.CotizacionRepuesto.orden_id == orden_id).all()
    for c in todas:
        c.aprobada_cliente = (c.id == cotizacion_id)

    total_aprobado = float(cot.precio) + float(cot.mano_obra)
    orden.costo_total = total_aprobado
    orden.repuestos_usados = f"{cot.nombre_repuesto} ({cot.marca}) - Prov: {cot.proveedor}"
    orden.estado = "Aprobado por Cliente"
    db.commit()
    db.refresh(orden)

    log = models.Trazabilidad(
        usuario=req.nombre_cliente or "Conductor",
        rol="Cliente",
        servicio=orden.tipo_servicio,
        vehiculo_id=orden.vehiculo_id,
        accion=f"APROBACION DIGITAL Ticket #{orden_id}: Autorizo proveedor {cot.proveedor} ({cot.nombre_repuesto}) por ${total_aprobado:,.0f}. Presupuesto bloqueado contra alteraciones."
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
    return db.query(models.Trazabilidad).order_by(models.Trazabilidad.id.desc()).all()
