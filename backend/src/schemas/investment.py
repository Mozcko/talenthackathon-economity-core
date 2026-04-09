from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class InstrumentoCatalogoResponse(BaseModel):
    id: int
    tipo: str
    entidad: str
    tasa_rendimiento_actual: Decimal
    monto_minimo_apertura: Decimal
    score_minimo_requerido: int
    beneficio_fiscal: bool
    model_config = ConfigDict(from_attributes=True)
 
class PortafolioInversionBase(BaseModel):
    saldo_invertido: Decimal

class PortafolioInversionCreate(PortafolioInversionBase):
    usuario_id: str
    instrumento_id: int
    tenant_id: UUID

class PortafolioInversionResponse(PortafolioInversionBase):
    id: UUID
    usuario_id: str
    instrumento_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)