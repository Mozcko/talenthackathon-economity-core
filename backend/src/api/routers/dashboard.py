# src/api/routers/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID

from src.core.database import get_db
from src.core.security import get_current_user_token
from src.schemas.dashboard import DashboardSummaryResponse
from src.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard y Resumen"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def obtener_resumen_dashboard(
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """
    Devuelve la 'fotografía' financiera actual del usuario para alimentar la pantalla principal.
    """
    tenant_id_str = token_payload.get("sub")
    if not tenant_id_str:
        raise HTTPException(status_code=400, detail="Token inválido")
        
    try:
        tenant_uuid = UUID(tenant_id_str) if '-' in tenant_id_str else tenant_id_str
        return dashboard_service.get_dashboard_summary(
            db=db, 
            tenant_id=tenant_uuid,
            user_id=tenant_id_str
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))