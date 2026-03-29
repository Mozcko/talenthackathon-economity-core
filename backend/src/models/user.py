import uuid
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.models.base import Base, AuditMixin

class Usuario(Base, AuditMixin):
    __tablename__ = "usuarios"

    # ID de Clerk (Suele ser un string como 'user_2xyz...')
    id = Column(String, primary_key=True, index=True) 
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    perfil_riesgo = Column(String, default="Moderado")
    flujo_caja_libre_mensual = Column(Numeric(12, 2), default=0.0)
    score_resiliencia = Column(Integer, default=0)

    # --- Relaciones Bidireccionales ---
    tenant = relationship("Tenant", back_populates="usuarios")
    cuentas = relationship("CuentaFinanciera", back_populates="usuario")
    portafolios = relationship("PortafolioInversion", back_populates="usuario")

class CuentaFinanciera(Base, AuditMixin):
    __tablename__ = "cuentas_financieras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    nombre = Column(String, nullable=False) # Ej: Efectivo, Nómina BBVA
    tipo = Column(String, nullable=False) # Debito, Credito, Efectivo
    saldo_actual = Column(Numeric(12, 2), default=0.0)

    # --- Relaciones Bidireccionales ---
    usuario = relationship("Usuario", back_populates="cuentas")
    tenant = relationship("Tenant", back_populates="cuentas")
    transacciones = relationship("Transaccion", back_populates="cuenta")