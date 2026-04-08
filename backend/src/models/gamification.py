import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.base import Base, AuditMixin

class PerfilGamificacion(Base, AuditMixin):
    """
    Perfil de gamificación por usuario.
    Almacena el estado actual de XP, nivel y rachas.
    """
    __tablename__ = "perfiles_gamificacion"

    usuario_id = Column(String, ForeignKey("usuarios.id"), primary_key=True, index=True)
    total_xp = Column(Integer, default=0, nullable=False)
    nivel_actual = Column(String, default="bronze", nullable=False)
    racha_actual = Column(Integer, default=0, nullable=False)
    racha_maxima = Column(Integer, default=0, nullable=False)
    fecha_ultima_actividad = Column(Date, nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="perfil_gamificacion")

class EventoGamificacion(Base, AuditMixin):
    """
    Registro histórico de eventos que otorgan XP o insignias.
    Sirve para auditoría e idempotencia.
    """
    __tablename__ = "eventos_gamificacion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False, index=True)
    tipo_evento = Column(String, nullable=False) # ej: "gasto_creado", "hito_racha"
    xp_otorgado = Column(Integer, default=0, nullable=False)
    referencia_id = Column(String, nullable=True) # ID de la entidad relacionada (ej: uuid de transaccion)
    metadatos = Column(JSON, nullable=True)

class DefinicionLogro(Base, AuditMixin):
    """
    Definición estática de logros/insignias disponibles.
    """
    __tablename__ = "definiciones_logros"

    codigo = Column(String, primary_key=True, index=True) # ej: "primer_gasto"
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    xp_recompensa = Column(Integer, default=0, nullable=False)
    criterios = Column(JSON, nullable=True) # Lógica para desbloqueo

    # Relaciones
    usuarios_con_logro = relationship("LogroUsuario", back_populates="definicion")

class LogroUsuario(Base, AuditMixin):
    """
    Relación de logros desbloqueados por cada usuario.
    """
    __tablename__ = "logros_usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False, index=True)
    codigo_logro = Column(String, ForeignKey("definiciones_logros.codigo"), nullable=False)
    desbloqueado_en = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    definicion = relationship("DefinicionLogro", back_populates="usuarios_con_logro")
    usuario = relationship("Usuario", back_populates="logros")
