import os
import ssl
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Obtener URL de entorno o usar local por defecto
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:@localhost:3306/taller_db"
)

# Asegurar dialecto pymysql
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Configurar argumentos de conexión (SSL para TiDB Cloud)
connect_args = {}
if "tidbcloud.com" in DATABASE_URL or "ssl" in DATABASE_URL.lower():
    # TiDB Cloud requiere SSL
    connect_args["ssl_verify_cert"] = True
    connect_args["ssl_verify_identity"] = True

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
