# src/schemas/goal.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class MetaFinancieraBase(BaseModel):
    nombre: str
    monto_objetivo: Decimal
    progreso_actual: Decimal = Decimal('0.0')
    fecha_limite: Optional[datetime] = None

class MetaFinancieraCreate(MetaFinancieraBase):
    usuario_id: str
    tenant_id: UUID

class MetaFinancieraResponse(MetaFinancieraBase):
    id: UUID
    usuario_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)