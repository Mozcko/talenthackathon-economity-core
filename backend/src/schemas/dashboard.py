# src/schemas/dashboard.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal

# Importamos los esquemas que ya teníamos para reutilizarlos
from src.schemas.goal import MetaFinancieraResponse
from src.schemas.investment import InstrumentoCatalogoResponse
 
class DashboardSummaryResponse(BaseModel):
    saldo_total: Decimal
    flujo_caja_mensual: Decimal
    score_resiliencia: int
    meta_proxima: Optional[MetaFinancieraResponse] = None
    mejor_oportunidad: Optional[InstrumentoCatalogoResponse] = None

    model_config = ConfigDict(from_attributes=True)