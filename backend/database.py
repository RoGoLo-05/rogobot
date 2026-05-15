"""
database.py — Configuración de la base de datos SQLite

SQLite es una base de datos que se guarda como un archivo local (.db).
No necesita servidor, se crea sola la primera vez que ejecutas la app.

ORM (Object Relational Mapper) nos permite
trabajar con la base de datos usando clases de Python en lugar de SQL puro.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")

# Creamos el motor de base de datos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Clase base
class Base(DeclarativeBase):
    pass


# MODELOS (tablas de la base de datos)
class User(Base):
    """
    Tabla 'users' — Almacena los usuarios del chatbot.
    Cada usuario tiene un perfil que el chatbot va actualizando.
    """
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    session_id    = Column(String(100), unique=True, index=True)
    name          = Column(String(100), nullable=True)
    message_count = Column(Integer, default=0)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen     = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    profile_json  = Column(Text, default="{}")


class Message(Base):
    """
    Tabla 'messages' — Historial de todos los mensajes.
    Cada fila es un mensaje (usuario o chatbot).
    """
    __tablename__ = "messages"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    role       = Column(String(10))
    content    = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    tokens_used = Column(Integer, nullable=True)
    emotion     = Column(String(50), nullable=True)


class PersonalitySnapshot(Base):
    """
    Tabla 'personality_snapshots' — Guarda cómo evoluciona la personalidad
    del chatbot con cada usuario a lo largo del tiempo.
    """
    __tablename__ = "personality_snapshots"

    id           = Column(Integer, primary_key=True, index=True)
    session_id   = Column(String(100), index=True)
    snapshot     = Column(Text)
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# FUNCIONES DE UTILIDAD
def create_tables():
    """Crea todas las tablas en la base de datos si no existen."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Generador de sesiones de base de datos.
    Se usa como dependencia en FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()