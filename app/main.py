from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from app.database import Base, engine, SessionLocal
import app.models as models
from app.routes import router
import bcrypt

Base.metadata.create_all(bind=engine)

def inicializar_datos():
    db = SessionLocal()
    try:
        usuarios_seed = [
            {"username": "cliente1", "nombre": "Carlos Mendoza (Conductor)", "rol": "Cliente", "pass": "12345"},
            {"username": "tecnico1", "nombre": "Andres Mecanico (Tecnico)", "rol": "Tecnico", "pass": "12345"},
            {"username": "asesor1", "nombre": "Camila Asesora (Taller)", "rol": "Asesor", "pass": "12345"}
        ]
        for u in usuarios_seed:
            existe = db.query(models.Usuario).filter(models.Usuario.username == u["username"]).first()
            if not existe:
                hashed = bcrypt.hashpw(u["pass"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                nuevo = models.Usuario(
                    username=u["username"],
                    password_hash=hashed,
                    nombre_completo=u["nombre"],
                    rol=u["rol"]
                )
                db.add(nuevo)
        db.commit()

        # Asegurar Cliente ID 1 para evitar error de llave foranea al registrar vehiculos
        cliente_base = db.query(models.Cliente).filter(models.Cliente.id == 1).first()
        if not cliente_base:
            cliente_base = models.Cliente(
                nombre="Carlos Mendoza",
                telefono="3001234567",
                email="carlos.mendoza@correo.com",
                documento="1020304050"
            )
            db.add(cliente_base)
            db.commit()
            db.refresh(cliente_base)

        # Crear vehiculo y orden de demostracion con 3 cotizaciones comparativas si no hay ninguno
        vehiculo_demo = db.query(models.Vehiculo).first()
        if not vehiculo_demo:
            vehiculo_demo = models.Vehiculo(
                placa="MKT-442",
                marca="Renault",
                modelo="Sandero 1.6",
                anio=2022,
                odometro=42500,
                cliente_id=cliente_base.id
            )
            db.add(vehiculo_demo)
            db.commit()
            db.refresh(vehiculo_demo)

            orden_demo = models.OrdenServicio(
                vehiculo_id=vehiculo_demo.id,
                tipo_servicio="Mantenimiento",
                diagnostico="Desgaste crítico en pastillas de freno delanteras y rectificación de discos",
                estado="Esperando Aprobación Cliente",
                costo_total=0.0,
                tecnico_asignado="Andres Mecanico (Tecnico)"
            )
            db.add(orden_demo)
            db.commit()
            db.refresh(orden_demo)

            cotizaciones_seed = [
                {"proveedor": "Autoshop SAS", "nombre_repuesto": "Kit Pastillas Delanteras Cerámica", "marca": "Brembo", "precio": 165000, "mano_obra": 80000},
                {"proveedor": "Casa Toro Repuestos", "nombre_repuesto": "Kit Pastillas Originales OEM", "marca": "Renault Genuine", "precio": 190000, "mano_obra": 80000},
                {"proveedor": "Mundimotos & Partes", "nombre_repuesto": "Kit Pastillas Semimetálicas", "marca": "TNK", "precio": 115000, "mano_obra": 80000}
            ]
            for c in cotizaciones_seed:
                db.add(models.CotizacionRepuesto(orden_id=orden_demo.id, **c))
            
            db.add(models.Trazabilidad(
                usuario="Camila Asesora (Taller)",
                rol="Asesor",
                servicio="Mantenimiento",
                vehiculo_id=vehiculo_demo.id,
                accion=f"Orden Cero Papel #{orden_demo.id} creada con 3 cotizaciones de proveedores para comparacion del conductor"
            ))
            db.commit()
    finally:
        db.close()

inicializar_datos()

app = FastAPI(
    title="MecaniClaro - Plataforma B2B2C de Gestion y Transparencia para Talleres",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.include_router(router)

@app.get("/")
def raiz():
    return RedirectResponse(url="/login")

@app.get("/login")
def pagina_login():
    return FileResponse("frontend/login.html")

@app.get("/cliente")
def pagina_cliente():
    return FileResponse("frontend/cliente.html")

@app.get("/tecnico")
def pagina_tecnico():
    return FileResponse("frontend/tecnico.html")

@app.get("/asesor")
def pagina_asesor():
    return FileResponse("frontend/asesor.html")

@app.get("/salud")
def salud():
    return {"estado": "OK", "plataforma": "MecaniClaro"}
