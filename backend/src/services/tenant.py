# src/services/tenant.py
from sqlalchemy.orm import Session
from uuid import UUID

from src.models.tenant import Tenant
from src.schemas.tenant import TenantCreate

def create_tenant(db: Session, tenant: TenantCreate) -> Tenant:
    """Crea una nueva organización/tenant en la base de datos."""
    db_tenant = Tenant(**tenant.model_dump())
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

def get_tenant(db: Session, tenant_id: UUID) -> Tenant:
    """Busca una organización por su ID."""
    return db.query(Tenant).filter(Tenant.id == tenant_id).first()