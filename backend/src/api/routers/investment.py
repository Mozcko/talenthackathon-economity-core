# src/api/routers/investment.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from uuid import UUID

from src.core.database import get_db
from src.core.security import get_current_user_token
from src.services import investment as investment_service
from src.schemas.investment import PortafolioInversionCreate, PortafolioInversionResponse

router = APIRouter(prefix="/inversiones", tags=["Inversiones y Portafolio"])

# --- ENDPOINT 1: TIER LIST ---

@router.get("/tierlist", summary="Generar Tier List Dinámica (Oportunidades)")
def obtener_tierlist_usuario(
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Evalúa hábitos y sugiere instrumentos reales basados en el score y flujo de caja."""
    tenant_id_str = token_payload.get("sub")
    if not tenant_id_str:
        raise HTTPException(status_code=400, detail="Token no contiene 'sub'")
        
    try:
        tenant_id = UUID(tenant_id_str) if isinstance(tenant_id_str, str) and '-' in tenant_id_str else tenant_id_str
        return investment_service.generar_tierlist_dinamica(
            db=db, 
            user_id=tenant_id_str,
            tenant_id=tenant_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ENDPOINTS 2 Y 3: MI PORTAFOLIO ---

@router.post("/portafolio", response_model=PortafolioInversionResponse, summary="Registrar nueva inversión")
def registrar_inversion(
    inversion: PortafolioInversionCreate,
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Añade una inversión a tu portafolio activo (ej. Invertir $1000 en Nu)."""
    tenant_id = token_payload.get("sub")
    
    # Zero-Trust: Aseguramos que la inversión quede a nombre del dueño del token
    inversion.tenant_id = UUID(tenant_id) if isinstance(tenant_id, str) and '-' in tenant_id else tenant_id
    inversion.usuario_id = str(tenant_id)
    
    return investment_service.create_inversion(db=db, inversion=inversion)

@router.get("/portafolio", response_model=List[PortafolioInversionResponse], summary="Ver mi portafolio")
def ver_mi_portafolio(
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Devuelve todo el historial de inversiones del usuario."""
    tenant_id = token_payload.get("sub")
    _tenant_uuid = UUID(tenant_id) if isinstance(tenant_id, str) and '-' in tenant_id else tenant_id
    
    return investment_service.get_portafolio_usuario(db=db, tenant_id=_tenant_uuid)