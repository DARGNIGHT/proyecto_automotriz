<<<<<<< HEAD
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from app.database import Base, engine, SessionLocal
import app.models as models
from app.routes import router
import bcrypt

Base.metadata.create_all(bind=engine)

def inicializar_usuarios():
    db = SessionLocal()
    try:
        usuarios_seed = [
            {"username": "cliente1", "nombre": "Carlos Mendoza (Cliente)", "rol": "Cliente", "pass": "12345"},
            {"username": "tecnico1", "nombre": "Andres Mecanico (Tecnico)", "rol": "Tecnico", "pass": "12345"},
            {"username": "asesor1", "nombre": "Camila Asesora (Asesor)", "rol": "Asesor", "pass": "12345"}
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
    finally:
        db.close()

inicializar_usuarios()

app = FastAPI(
    title="Sistema de Gestion para Taller Automotriz",
    version="1.0.0"
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

# Redireccion raíz al login
@app.get("/")
def raiz():
    return RedirectResponse(url="/login")

# Rutas dedicadas por modulo
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
    return {"estado": "OK"}
=======
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from app.database import Base, engine, SessionLocal
import app.models as models
from app.routes import router
import bcrypt

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Aviso BD al iniciar: {e}")

def inicializar_usuarios():
    db = SessionLocal()
    try:
        usuarios_seed = [
            {"username": "cliente1", "nombre": "Carlos Mendoza (Cliente)", "rol": "Cliente", "pass": "12345"},
            {"username": "tecnico1", "nombre": "Andres Mecanico (Tecnico)", "rol": "Tecnico", "pass": "12345"},
            {"username": "asesor1", "nombre": "Camila Asesora (Asesor)", "rol": "Asesor", "pass": "12345"}
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
    finally:
        db.close()

inicializar_usuarios()

app = FastAPI(
    title="Sistema de Gestion para Taller Automotriz",
    version="1.0.0"
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

# Redireccion raíz al login
@app.get("/")
def raiz():
    return RedirectResponse(url="/login")

# Rutas dedicadas por modulo
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
    return {"estado": "OK"}
>>>>>>> be3331f48e28d95f66a3b7a6bfdd7498a5a201ae
