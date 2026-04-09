from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class TransaccionBase(BaseModel):
    monto: Decimal
    fecha_operacion: datetime
    descripcion: Optional[str] = None

class TransaccionCreate(TransaccionBase):
    cuenta_id: UUID
    sub_categoria_id: Optional[int] = None
    tenant_id: UUID

class TransaccionResponse(TransaccionBase):
    id: UUID
    cuenta_id: UUID
    sub_categoria_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)