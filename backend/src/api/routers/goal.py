# src/api/routers/goal.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID
from decimal import Decimal

from src.core.database import get_db
from src.core.security import get_current_user_token
from src.schemas.goal import MetaFinancieraCreate, MetaFinancieraResponse
from src.services import goal as goal_service

router = APIRouter(prefix="/metas", tags=["Metas Financieras"])

@router.post("/", response_model=MetaFinancieraResponse)
def crear_nueva_meta(
    meta: MetaFinancieraCreate,
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Crea una meta asociada al usuario autenticado (Zero-Trust)."""
    tenant_id = token_payload.get("sub")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Token no contiene 'sub' (tenant_id)")
    
    # Inyectamos de forma segura el ID del usuario extraído del Token
    meta.tenant_id = UUID(tenant_id) if isinstance(tenant_id, str) and '-' in tenant_id else tenant_id
    meta.usuario_id = str(tenant_id)
    
    return goal_service.create_meta(db=db, meta=meta)

@router.get("/", response_model=List[MetaFinancieraResponse])
def listar_mis_metas(
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Retorna todas las metas del usuario."""
    tenant_id = token_payload.get("sub")
    _tenant_uuid = UUID(tenant_id) if isinstance(tenant_id, str) and '-' in tenant_id else tenant_id
    return goal_service.get_metas_by_usuario(db=db, tenant_id=_tenant_uuid)

@router.patch("/{meta_id}/progreso", response_model=MetaFinancieraResponse)
def agregar_progreso_meta(
    meta_id: UUID,
    monto_a_sumar: Decimal = Query(..., description="Cantidad de dinero para sumar a la meta"),
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Agrega fondos a una meta específica."""
    tenant_id = token_payload.get("sub")
    _tenant_uuid = UUID(tenant_id) if isinstance(tenant_id, str) and '-' in tenant_id else tenant_id
    
    meta_actualizada = goal_service.add_progreso_meta(db, meta_id, monto_a_sumar, _tenant_uuid)
    if not meta_actualizada:
        raise HTTPException(status_code=404, detail="La meta no existe o no te pertenece")
        
    return meta_actualizada

@router.delete("/{meta_id}")
def borrar_meta(
    meta_id: UUID,
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Elimina una meta del perfil del usuario."""
    tenant_id = token_payload.get("sub")
    _tenant_uuid = UUID(tenant_id) if isinstance(tenant_id, str) and '-' in tenant_id else tenant_id
    
    eliminado = goal_service.delete_meta(db, meta_id, _tenant_uuid)
    if not eliminado:
        raise HTTPException(status_code=404, detail="La meta no existe o no te pertenece")
        
    return {"status": "success", "detail": "Meta eliminada correctamente"}