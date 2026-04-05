# src/api/routers/tenant.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID

from src.core.database import get_db
from src.core.security import get_current_user_token
from src.schemas.tenant import TenantCreate, TenantResponse
from src.services import tenant as tenant_service

router = APIRouter(prefix="/organizaciones", tags=["Organizaciones (Tenants)"])

@router.post("/", response_model=TenantResponse)
def registrar_organizacion(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
    # Nota: Aquí podríamos usar la dependencia @require_admin que hicimos antes, 
    # pero para el MVP dejaremos que cualquier usuario logueado cree su entorno.
    token_payload: Dict[str, Any] = Depends(get_current_user_token) 
):
    """Crea un nuevo entorno o familia (Tenant)."""
    return tenant_service.create_tenant(db=db, tenant=tenant)

@router.get("/mi-organizacion", response_model=TenantResponse)
def obtener_mi_entorno(
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """Devuelve los datos de la organización asociada al token actual."""
    tenant_id_str = token_payload.get("sub")
    if not tenant_id_str:
        raise HTTPException(status_code=400, detail="Token inválido")
        
    try:
        # Asumimos que para este MVP el 'sub' del JWT actúa como el tenant_id
        tenant_uuid = UUID(tenant_id_str) if '-' in tenant_id_str else UUID(tenant_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="El identificador de la organización no tiene un formato válido.")

    tenant_db = tenant_service.get_tenant(db=db, tenant_id=tenant_uuid)
    if not tenant_db:
        raise HTTPException(status_code=404, detail="Organización no encontrada en la base de datos")
        
    return tenant_db