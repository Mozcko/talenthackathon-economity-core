from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

# --- USUARIO ---
class UsuarioBase(BaseModel):
    perfil_riesgo: str = "Moderado"
    flujo_caja_libre_mensual: Decimal = Decimal('0.0')
    score_resiliencia: int = 0
 
class UsuarioCreate(UsuarioBase):
    id: str # Llega desde Clerk
    tenant_id: UUID

class UsuarioResponse(UsuarioBase):
    id: str
    tenant_id: UUID
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

# --- CUENTA FINANCIERA ---
class CuentaFinancieraBase(BaseModel):
    nombre: str
    tipo: str
    saldo_actual: Decimal

class CuentaFinancieraCreate(CuentaFinancieraBase):
    usuario_id: str
    tenant_id: UUID

class CuentaFinancieraResponse(CuentaFinancieraBase):
    id: UUID
    usuario_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)