from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.security import get_current_user_token
from src.schemas.gamification import (
    PerfilGamificacionResponse,
    LogroUsuarioResponse,
    HitoResponse
)
from src.services import gamification as gamification_service
from src.models.gamification import LogroUsuario

router = APIRouter(prefix="/gamification", tags=["Gamificación"])

@router.get("/profile", response_model=PerfilGamificacionResponse)
def get_user_profile(
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Obtiene el perfil de gamificación del usuario actual."""
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido")

    return gamification_service.get_calculated_profile(db, user_id=user_id)

@router.get("/achievements", response_model=List[LogroUsuarioResponse])
def get_user_achievements(
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Obtiene los logros desbloqueados por el usuario."""
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido")

    logros = db.query(LogroUsuario).filter(LogroUsuario.usuario_id == user_id).all()
    return logros

@router.get("/next-milestone", response_model=HitoResponse)
def get_next_milestone(
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Obtiene el siguiente hito o recomendación para el usuario."""
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido")

    return gamification_service.get_next_milestone(db, user_id=user_id)
