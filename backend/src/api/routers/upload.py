import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user_token
from src.services.ai.agents import extraction_agent

router = APIRouter(prefix="/upload", tags=["Extracción de Transacciones (IA)"])

class TextoPayload(BaseModel):
    texto: str


def _resolve_sub_categoria_id(db: Session, categoria_sugerida: str, es_ingreso: bool) -> int | None:
    """
    Map the AI-suggested category to a sub_categoria id, respecting income vs expense.
    """
    from src.models.transaction import SubCategoria, Categoria

    tipo_flujo = "Ingreso" if es_ingreso else "Egreso"

    # 1. Try partial match within the correct flow type
    sub_cat = (
        db.query(SubCategoria)
        .join(Categoria, SubCategoria.categoria_id == Categoria.id)
        .filter(
            Categoria.tipo_flujo == tipo_flujo,
            SubCategoria.nombre.ilike(f"%{categoria_sugerida}%"),
        )
        .first()
    )

    # 2. Fallback: first sub_categoria of the correct flow type
    if not sub_cat:
        sub_cat = (
            db.query(SubCategoria)
            .join(Categoria, SubCategoria.categoria_id == Categoria.id)
            .filter(Categoria.tipo_flujo == tipo_flujo)
            .first()
        )

    return sub_cat.id if sub_cat else None


@router.post("/texto")
async def procesar_texto(
    payload: TextoPayload,
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Recibe texto, usa el Agente IA para extraer monto y descripción, y lo devuelve al frontend."""
    try:
        datos = await extraction_agent.extraer_datos_texto_async(payload.texto)
        datos["sub_categoria_id"] = _resolve_sub_categoria_id(db, datos.get("categoria_sugerida", ""), datos.get("es_ingreso", False))
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio")
async def procesar_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Recibe un audio, lo transcribe con Whisper, extrae la transacción y lo devuelve al frontend."""
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        datos = await extraction_agent.extraer_datos_audio_async(temp_path)
        datos["sub_categoria_id"] = _resolve_sub_categoria_id(db, datos.get("categoria_sugerida", ""), datos.get("es_ingreso", False))
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando audio: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/imagen")
async def procesar_imagen(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Recibe un ticket o recibo en imagen, usa Visión para extraer la transacción y lo devuelve al frontend."""
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        datos = await extraction_agent.extraer_datos_imagen_async(temp_path)
        datos["sub_categoria_id"] = _resolve_sub_categoria_id(db, datos.get("categoria_sugerida", ""), datos.get("es_ingreso", False))
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
