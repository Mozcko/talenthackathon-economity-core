import uuid
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.models.base import Base, AuditMixin

class Categoria(Base, AuditMixin):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String, nullable=False) # Taxonomía Macro
    tipo_flujo = Column(String, nullable=False) # Ingreso, Egreso

    # --- Relaciones Bidireccionales ---
    sub_categorias = relationship("SubCategoria", back_populates="categoria")

class SubCategoria(Base, AuditMixin):
    __tablename__ = "sub_categorias"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    nombre = Column(String, nullable=False) # Taxonomía Micro

    # --- Relaciones Bidireccionales ---
    categoria = relationship("Categoria", back_populates="sub_categorias")
    transacciones = relationship("Transaccion", back_populates="sub_categoria")

class Transaccion(Base, AuditMixin):
    __tablename__ = "transacciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cuenta_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_financieras.id"), nullable=False)
    sub_categoria_id = Column(Integer, ForeignKey("sub_categorias.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    monto = Column(Numeric(12, 2), nullable=False)
    fecha_operacion = Column(DateTime(timezone=True), nullable=False)
    descripcion = Column(String, nullable=True) # Extraída por la IA

    # --- Relaciones Bidireccionales ---
    cuenta = relationship("CuentaFinanciera", back_populates="transacciones")
    sub_categoria = relationship("SubCategoria", back_populates="transacciones")
    tenant = relationship("Tenant", back_populates="transacciones")