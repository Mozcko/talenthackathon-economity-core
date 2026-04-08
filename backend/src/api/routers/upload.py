import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, Any
from pydantic import BaseModel

from src.core.security import get_current_user_token
from src.services.ai.agents import extraction_agent

router = APIRouter(prefix="/upload", tags=["Extracción de Transacciones (IA)"])

class TextoPayload(BaseModel):
    texto: str

@router.post("/texto")
async def procesar_texto(
    payload: TextoPayload,
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Recibe texto, usa el Agente IA para extraer monto y descripción, y lo devuelve al frontend."""
    try:
        datos = await extraction_agent.extraer_datos_texto_async(payload.texto)
        return {"status": "success", "data": datos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio")
async def procesar_audio(
    file: UploadFile = File(...),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Recibe un audio, lo transcribe con Whisper, extrae la transacción y lo devuelve al frontend."""
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        datos = await extraction_agent.extraer_datos_audio_async(temp_path)
        return {"status": "success", "data": datos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando audio: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/imagen")
async def procesar_imagen(
    file: UploadFile = File(...),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Recibe un ticket o recibo en imagen, usa Visión para extraer la transacción y lo devuelve al frontend."""
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        datos = await extraction_agent.extraer_datos_imagen_async(temp_path)
        return {"status": "success", "data": datos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)