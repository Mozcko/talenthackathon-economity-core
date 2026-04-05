# src/api/routes/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.core.database import get_db
from src.schemas.user import (
    UsuarioCreate, UsuarioResponse, 
    CuentaFinancieraCreate, CuentaFinancieraResponse
)
from src.services import user as user_service

# Creamos un router para agrupar todas las rutas relacionadas con usuarios
router = APIRouter(prefix="/usuarios", tags=["Usuarios y Cuentas"])

@router.post("/", response_model=UsuarioResponse)
def create_usuario(user: UsuarioCreate, db: Session = Depends(get_db)):
    """Crea un usuario nuevo."""
    # Verificamos si el usuario ya existe para no duplicarlo
    db_user = user_service.get_usuario(db, user_id=user.id)
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya está registrado")
    return user_service.create_usuario(db=db, user=user)

@router.get("/{user_id}", response_model=UsuarioResponse)
def read_usuario(user_id: str, db: Session = Depends(get_db)):
    """Obtiene los detalles de un usuario."""
    db_user = user_service.get_usuario(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

@router.post("/{user_id}/cuentas/", response_model=CuentaFinancieraResponse)
def create_cuenta_para_usuario(
    user_id: str, 
    cuenta: CuentaFinancieraCreate, 
    db: Session = Depends(get_db)
):
    """Crea una cuenta financiera asociada a un usuario."""
    # Nos aseguramos de que el usuario exista
    db_user = user_service.get_usuario(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Aseguramos que el ID de usuario en la ruta coincida con el del body
    cuenta.usuario_id = user_id 
    return user_service.create_cuenta_financiera(db=db, cuenta=cuenta)

@router.get("/{user_id}/cuentas/", response_model=List[CuentaFinancieraResponse])
def read_cuentas_usuario(user_id: str, db: Session = Depends(get_db)):
    """Obtiene todas las cuentas de un usuario."""
    return user_service.get_cuentas_by_usuario(db, user_id=user_id)