from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UsuarioCreate(BaseModel):
    username: str
    password: str
    nombre_completo: str
    rol: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    username: str
    nombre_completo: str
    rol: str
    mensaje: str

class ClienteBase(BaseModel):
    nombre: str
    telefono: str
    email: Optional[str] = None
    documento: str

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    class Config:
        from_attributes = True

class VehiculoBase(BaseModel):
    placa: str
    marca: str
    modelo: str
    anio: int
    odometro: Optional[int] = 0
    cliente_id: int

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoResponse(VehiculoBase):
    id: int
    class Config:
        from_attributes = True

class CotizacionCreate(BaseModel):
    proveedor: str
    nombre_repuesto: str
    marca: str
    precio: float
    mano_obra: Optional[float] = 0.0
    usuario_responsable: Optional[str] = "Asesor"

class CotizacionResponse(BaseModel):
    id: int
    orden_id: int
    proveedor: str
    nombre_repuesto: str
    marca: str
    precio: float
    mano_obra: float
    aprobada_cliente: bool
    fecha: datetime
    class Config:
        from_attributes = True

class AprobacionClienteRequest(BaseModel):
    nombre_cliente: str

class OrdenBase(BaseModel):
    vehiculo_id: int
    tipo_servicio: Optional[str] = "Mantenimiento"
    diagnostico: str
    estado: Optional[str] = "Solicitado"
    costo_total: Optional[float] = 0.0

class OrdenCreate(OrdenBase):
    rol_solicitante: Optional[str] = "Cliente"
    nombre_solicitante: Optional[str] = "Usuario"

class OrdenUpdateOperativo(BaseModel):
    estado: str
    rol_responsable: str
    nombre_responsable: str
    tecnico_asignado: Optional[str] = None
    checklist_tecnico: Optional[str] = None
    repuestos_usados: Optional[str] = None
    dictamen_garantia: Optional[str] = None
    costo_total: Optional[float] = None
    observacion: Optional[str] = None

class OrdenResponse(OrdenBase):
    id: int
    fecha_creacion: datetime
    tecnico_asignado: Optional[str] = "Por Asignar"
    checklist_tecnico: Optional[str] = "Pendiente"
    repuestos_usados: Optional[str] = "Ninguno"
    dictamen_garantia: Optional[str] = "No Aplica"
    class Config:
        from_attributes = True

class MensajeCreate(BaseModel):
    remitente: str
    rol: str
    mensaje: str

class MensajeResponse(BaseModel):
    id: int
    orden_id: int
    remitente: str
    rol: str
    mensaje: str
    fecha: datetime
    class Config:
        from_attributes = True

class TrazabilidadResponse(BaseModel):
    id: int
    usuario: str
    rol: str
    fecha: datetime
    servicio: str
    vehiculo_id: int
    accion: str
    class Config:
        from_attributes = True
