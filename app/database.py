import os
import ssl
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Obtener URL de conexión
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:@localhost:3306/taller_db"
)

# Convertir mysql:// a mysql+pymysql://
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Remover parámetros de query si vienen en la URL para evitar conflictos
clean_url = DATABASE_URL.split("?")[0]

connect_args = {}

# Si es conexión a TiDB Cloud, configurar SSL con los certificados del sistema
if "tidbcloud.com" in clean_url:
    ca_path = "/etc/ssl/certs/ca-certificates.crt"  # Ruta estándar en Ubuntu/Debian/Render
    if os.path.exists(ca_path):
        connect_args["ssl"] = {"ca": ca_path}
    else:
        # Fallback para Windows o entornos locales
        ctx = ssl.create_default_context()
        connect_args["ssl"] = ctx

engine = create_engine(
    clean_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
