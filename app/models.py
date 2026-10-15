from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    rol = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    documento = Column(String(20), unique=True, index=True, nullable=False)

    vehiculos = relationship("Vehiculo", back_populates="cliente")

class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), unique=True, index=True, nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    anio = Column(Integer, nullable=False)
    odometro = Column(Integer, default=0)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    cliente = relationship("Cliente", back_populates="vehiculos")
    ordenes = relationship("OrdenServicio", back_populates="vehiculo")
    auditorias = relationship("Trazabilidad", back_populates="vehiculo")

class OrdenServicio(Base):
    __tablename__ = "ordenes_servicio"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    tipo_servicio = Column(String(30), default="Mantenimiento", nullable=False)
    diagnostico = Column(Text, nullable=False)
    estado = Column(String(30), default="Solicitado")
    costo_total = Column(Numeric(10, 2), default=0.0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    tecnico_asignado = Column(String(100), default="Por Asignar")
    checklist_tecnico = Column(String(255), default="Pendiente")
    repuestos_usados = Column(Text, default="Ninguno")
    dictamen_garantia = Column(String(100), default="No Aplica")

    vehiculo = relationship("Vehiculo", back_populates="ordenes")
    mensajes = relationship("MensajeNovedad", back_populates="orden")

class MensajeNovedad(Base):
    __tablename__ = "mensajes_novedad"

    id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey("ordenes_servicio.id"), nullable=False)
    remitente = Column(String(100), nullable=False)
    rol = Column(String(20), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    orden = relationship("OrdenServicio", back_populates="mensajes")

class Trazabilidad(Base):
    __tablename__ = "trazabilidad"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(100), nullable=False)
    rol = Column(String(30), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    servicio = Column(String(30), nullable=False)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    accion = Column(String(255), nullable=False)

    vehiculo = relationship("Vehiculo", back_populates="auditorias")
