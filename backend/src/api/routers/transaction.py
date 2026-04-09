# src/api/routes/transaction.py
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user_token
from src.schemas.transaction import TransaccionCreate, TransaccionResponse
from src.services import transaction as transaction_service
from src.services.category import resolve_sub_categoria_id

# Importamos nuestro ecosistema de IA desde la nueva ubicación segura
from src.services.ai import multimodal_parser as ai_service

router = APIRouter(prefix="/transacciones", tags=["Transacciones"])


def _get_tenant_id(db: Session, user_id: str) -> UUID:
    """Resolve the tenant UUID for a Clerk user ID via DB lookup."""
    from src.models.user import Usuario
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user.tenant_id

# --- RUTAS CRUD TRADICIONALES ---

@router.post("/", response_model=TransaccionResponse)
def create_transaccion(
    transaccion: TransaccionCreate, 
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """
    Registra una nueva transacción financiera (ingreso o egreso) manualmente.
    Requiere autenticación Bearer (JWT).
    """
    # Zero-Trust: resolve tenant UUID from the authenticated user record
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido: no contiene 'sub'")
    transaccion.tenant_id = _get_tenant_id(db, user_id)
    
    return transaction_service.create_transaccion(db=db, transaccion=transaccion)

@router.get("/cuenta/{cuenta_id}", response_model=List[TransaccionResponse])
def read_transacciones_cuenta(
    cuenta_id: UUID, 
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """
    Obtiene el historial completo de transacciones de una cuenta específica.
    """
    # Nota: En un sistema de producción estricto, aquí también verificaríamos
    # que la cuenta solicitada pertenezca al tenant_id del token_payload.
    transacciones = transaction_service.get_transacciones_by_cuenta(db, cuenta_id=cuenta_id)
    return transacciones

# --- RUTAS ZERO-FRICTION (IA) ---

@router.post("/cuenta/{cuenta_id}/audio", response_model=TransaccionResponse)
def registrar_transaccion_por_voz(
    cuenta_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """
    [Zero-Friction] Recibe un audio dictado por el usuario, lo transcribe con Whisper, 
    extrae los datos estructurados con GPT-4o y registra la transacción en la base de datos.
    """
    # 1. Zero-Trust: resolve tenant UUID from the authenticated user record
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token no contiene 'sub'")
    tenant_uuid = _get_tenant_id(db, user_id)

    # 2. Guardar el archivo temporalmente en disco para que Whisper lo pueda leer
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 3. Enviar a Whisper (Speech-to-Text)
        texto_transcrito = ai_service.transcribir_audio(temp_file_path)
        print(f"🎙️ Transcripción exitosa: '{texto_transcrito}'") # Log útil para desarrollo
        
        # 4. Extraer Datos Estructurados (LangChain + GPT-4o)
        datos_ia = ai_service.extraer_datos_financieros(texto_transcrito)
        
        # 5. Preparar el schema para guardar en Base de Datos
        nueva_transaccion = TransaccionCreate(
            cuenta_id=cuenta_id,
            sub_categoria_id=resolve_sub_categoria_id(db, datos_ia.categoria_sugerida, datos_ia.es_ingreso),
            tenant_id=tenant_uuid,
            monto=datos_ia.monto if datos_ia.es_ingreso else -datos_ia.monto,
            fecha_operacion=datetime.now(),
            descripcion=datos_ia.descripcion
        )

        # 6. Persistir en la base de datos relacional
        db_res = transaction_service.create_transaccion(db=db, transaccion=nueva_transaccion)

        # 7. Bono Extra por Zero-Friction (IA)
        from src.services import gamification as gamification_service
        gamification_service.award_xp(
            db, 
            user_id=user_id, 
            amount=5, 
            event_type="audio_log_bonus", 
            reference_id=str(db_res.id)
        )
        
        return db_res
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en IA o guardado: {str(e)}")
    finally:
        # 8. Limpieza: Borrar el archivo temporal siempre, incluso si hubo errores
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post("/cuenta/{cuenta_id}/imagen", response_model=TransaccionResponse)
def registrar_transaccion_por_ticket(
    cuenta_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """
    [Zero-Friction] Recibe la foto de un ticket, extrae los datos con GPT-4o Vision 
    y registra el gasto automáticamente.
    """
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido")
    tenant_uuid = _get_tenant_id(db, user_id)

    # Guardar imagen temporalmente
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Usar la función de visión que ya tenemos en multimodal_parser
        datos_ia = ai_service.extraer_datos_de_imagen(temp_file_path)
        
        nueva_transaccion = TransaccionCreate(
            cuenta_id=cuenta_id,
            sub_categoria_id=resolve_sub_categoria_id(db, datos_ia.categoria_sugerida, datos_ia.es_ingreso),
            tenant_id=tenant_uuid,
            monto=datos_ia.monto if datos_ia.es_ingreso else -datos_ia.monto,
            fecha_operacion=datetime.now(),
            descripcion=datos_ia.descripcion
        )

        # Persistir
        db_res = transaction_service.create_transaccion(db=db, transaccion=nueva_transaccion)

        # Bono Extra Vision (IA)
        from src.services import gamification as gamification_service
        gamification_service.award_xp(
            db, 
            user_id=user_id, 
            amount=10, 
            event_type="image_log_bonus", 
            reference_id=str(db_res.id)
        )
        
        return db_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al analizar el ticket: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.delete("/{transaccion_id}")
def borrar_transaccion(
    transaccion_id: UUID,
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Elimina una transacción en caso de error (requiere validación de dueño)."""
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido")
    tenant_uuid = _get_tenant_id(db, user_id)
    
    # Buscamos la transacción validando que pertenezca al usuario
    from src.models.transaction import Transaccion
    transaccion = db.query(Transaccion).filter(
        Transaccion.id == transaccion_id,
        Transaccion.tenant_id == tenant_uuid
    ).first()
    
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada o no te pertenece")
        
    db.delete(transaccion)
    db.commit()
    return {"status": "success", "detail": "Transacción eliminada"}