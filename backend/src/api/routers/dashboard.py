# src/api/routers/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.core.database import get_db
from src.core.security import get_current_user_token
from src.models.user import Usuario
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
    clerk_user_id = token_payload.get("sub")
    if not clerk_user_id:
        raise HTTPException(status_code=400, detail="Token inválido")

    usuario = db.query(Usuario).filter(Usuario.id == clerk_user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    try:
        return dashboard_service.get_dashboard_summary(
            db=db,
            tenant_id=usuario.tenant_id,
            user_id=clerk_user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))