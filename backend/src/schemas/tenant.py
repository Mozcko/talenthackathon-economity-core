# src/schemas/tenant.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class TenantBase(BaseModel):
    nombre: str

class TenantCreate(TenantBase):
    model_config = ConfigDict(extra="ignore")  # silently drops plan_suscripcion sent by frontend

class TenantResponse(TenantBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)