import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.models.base import Base, AuditMixin

class Tenant(Base, AuditMixin):
    """
    Entidad raíz para el aislamiento Zero-Trust (SaaS).
    Coincide con el Organization ID si usas Clerk B2B, o aisla cuentas individuales.
    """
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String, nullable=True) # Opcional: Nombre de la organización/entorno

    # --- Relaciones Bidireccionales ---
    usuarios = relationship("Usuario", back_populates="tenant")
    cuentas = relationship("CuentaFinanciera", back_populates="tenant")
    transacciones = relationship("Transaccion", back_populates="tenant")
    portafolios = relationship("PortafolioInversion", back_populates="tenant")