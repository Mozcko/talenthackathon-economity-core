# src/models/goal.py
import uuid
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.models.base import Base, AuditMixin

class MetaFinanciera(Base, AuditMixin):
    __tablename__ = "metas_financieras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    nombre = Column(String, nullable=False) # Ej: Enganche de auto, Fondo de emergencia
    monto_objetivo = Column(Numeric(12, 2), nullable=False)
    progreso_actual = Column(Numeric(12, 2), default=0.0)
    fecha_limite = Column(DateTime(timezone=True), nullable=True)

    # --- Relaciones Bidireccionales ---
    usuario = relationship("Usuario", back_populates="metas")