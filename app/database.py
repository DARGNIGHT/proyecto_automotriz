import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:@localhost:3306/taller_db"
)

# Convertir mysql:// a mysql+pymysql://
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Limpiar parámetros sobrantes en la URL si los hubiera
clean_url = DATABASE_URL.split("?")[0]

connect_args = {}
# TiDB Cloud Serverless requiere SSL para PyMySQL
if "tidbcloud.com" in clean_url:
    connect_args = {
        "ssl_verify_cert": True,
        "ssl_verify_identity": True
    }

engine = create_engine(
    clean_url,
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
