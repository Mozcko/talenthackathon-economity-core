# src/schemas/tenant.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class TenantBase(BaseModel):
    nombre: str
    plan_suscripcion: Optional[str] = "gratis" # Para un futuro modelo SaaS

class TenantCreate(TenantBase):
    pass

class TenantResponse(TenantBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)