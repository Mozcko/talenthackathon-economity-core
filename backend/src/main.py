import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
import requests

from src.core.config import settings
from src.core.database import get_db, engine

from src.models.base import Base
import src.models

from src.api.routers import user as user_routes
from src.api.routers import chat as chat_routes
from src.api.routers import investment as investment_routes
from src.api.routers import transaction as transaction_routes
from src.api.routers import goal as goal_routes
from src.api.routers import category as category_routes
from src.api.routers import tenant as tenant_routes
from src.api.routers import dashboard as dashboard_routes
from src.api.routers import gamification as gamification_routes
from src.api.routers import upload as upload_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Wait for DB to be ready before creating tables
    for attempt in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Base de datos lista.")
            break
        except Exception as e:
            if attempt == 9:
                raise RuntimeError(f"No se pudo conectar a la base de datos después de 10 intentos: {e}") from e
            print(f"⏳ Esperando DB (intento {attempt + 1}/10): {e}")
            time.sleep(3)
    yield


# Inicialización de la aplicación FastAPI
app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

# Inclusión de Routers
app.include_router(user_routes.router)
app.include_router(transaction_routes.router)
app.include_router(investment_routes.router)
app.include_router(chat_routes.router)
app.include_router(goal_routes.router)
app.include_router(category_routes.router)
app.include_router(tenant_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(gamification_routes.router)
app.include_router(upload_routes.router)

# --- RUTAS GENERALES ---

@app.get("/", tags=["General"])
def read_root():
    """
    Endpoint raíz para verificar que la API está levantada.
    """
    return {
        "status": "ok", 
        "message": f"🚀 Bienvenido a la API de {settings.app_title}",
        "version": settings.app_version
    }

@app.get("/health", tags=["General"])
def health_check(db: Session = Depends(get_db)):
    """
    Endpoint de Health Check (Crucial para entornos Cloud/AWS).
    Verifica la conexión tanto a la base de datos relacional (PostgreSQL) 
    como a la base de datos vectorial (ChromaDB).
    """
    # 1. Revisar conexión a PostgreSQL (Datos Transaccionales)
    try:
        db.execute(text("SELECT 1"))
        pg_status = "Conectado 🟢"
    except Exception as e:
        pg_status = f"Error 🔴: {str(e)}"

    # 2. Revisar conexión a ChromaDB (Base Vectorial para RAG)
    try:
        response = requests.get(f"{settings.chroma_url}/api/v2/heartbeat", timeout=5)
        if response.status_code == 200:
            chroma_status = "Conectado 🟢"
        else:
            chroma_status = f"Error 🔴: HTTP {response.status_code} - {response.text}"
    except Exception as e:
        chroma_status = f"Error 🔴: No se pudo conectar ({str(e)})"

    return {
        "api_status": "ok 🟢",
        "postgresql_status": pg_status,
        "chromadb_status": chroma_status
    }
