from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.sql import func

Base = declarative_base()

class AuditMixin:
    """ 
    Mixin que agrega automáticamente columnas de auditoría.
    Garantiza trazabilidad en todos los registros financieros.
    """
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)