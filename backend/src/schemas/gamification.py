from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class LogroBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: str
    xp_recompensa: int

class LogroResponse(LogroBase):
    model_config = ConfigDict(from_attributes=True)

class LogroUsuarioResponse(BaseModel):
    codigo_logro: str
    desbloqueado_en: datetime
    definicion: LogroResponse

    model_config = ConfigDict(from_attributes=True)

class PerfilGamificacionResponse(BaseModel):
    usuario_id: str
    total_xp: int
    nivel_actual: str
    racha_actual: int
    racha_maxima: int
    fecha_ultima_actividad: Optional[date]

    # Campos calculados para el frontend
    siguiente_nivel: Optional[str] = None
    xp_para_siguiente_nivel: Optional[int] = None
    porcentaje_progreso: float = 0.0

    model_config = ConfigDict(from_attributes=True)

class HitoResponse(BaseModel):
    mensaje: str
    xp_objetivo: Optional[int] = None
    progreso: float
    completado: bool
