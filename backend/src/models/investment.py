import uuid
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.models.base import Base, AuditMixin

class InstrumentoCatalogo(Base, AuditMixin):
    __tablename__ = "instrumentos_catalogo"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    tipo = Column(String, nullable=False) # SOFIPO, PPR, CETES
    entidad = Column(String, nullable=False) # Finsus, Nu, etc.
    
    tasa_rendimiento_actual = Column(Numeric(6, 4), nullable=False) # Ej: 0.1009 (10.09%)
    monto_minimo_apertura = Column(Numeric(12, 2), nullable=False)
    score_minimo_requerido = Column(Integer, nullable=False)
    beneficio_fiscal = Column(Boolean, default=False)

    # --- Relaciones Bidireccionales ---
    portafolios = relationship("PortafolioInversion", back_populates="instrumento")

class PortafolioInversion(Base, AuditMixin):
    __tablename__ = "portafolios_inversion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False)
    instrumento_id = Column(Integer, ForeignKey("instrumentos_catalogo.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    saldo_invertido = Column(Numeric(12, 2), default=0.0)

    # --- Relaciones Bidireccionales ---
    usuario = relationship("Usuario", back_populates="portafolios")
    instrumento = relationship("InstrumentoCatalogo", back_populates="portafolios")
    tenant = relationship("Tenant", back_populates="portafolios")