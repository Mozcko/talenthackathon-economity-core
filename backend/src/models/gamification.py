import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.base import Base, AuditMixin

class UserGamificationProfile(Base, AuditMixin):
    """
    Perfil de gamificación por usuario.
    Almacena el estado actual de XP, nivel y rachas.
    """
    __tablename__ = "user_gamification_profiles"

    user_id = Column(String, ForeignKey("usuarios.id"), primary_key=True, index=True)
    total_xp = Column(Integer, default=0, nullable=False)
    current_tier = Column(String, default="bronze", nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    max_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(Date, nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="gamification_profile")

class GamificationEvent(Base, AuditMixin):
    """
    Registro histórico de eventos que otorgan XP o insignias.
    Sirve para auditoría e idempotencia.
    """
    __tablename__ = "gamification_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(String, ForeignKey("usuarios.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False) # ej: "expense_created", "streak_milestone"
    xp_awarded = Column(Integer, default=0, nullable=False)
    reference_id = Column(String, nullable=True) # ID de la entidad relacionada (ej: uuid de transaccion)
    metadata_json = Column(JSON, nullable=True)

class AchievementDefinition(Base, AuditMixin):
    """
    Definición estática de logros/insignias disponibles.
    """
    __tablename__ = "achievement_definitions"

    code = Column(String, primary_key=True, index=True) # ej: "first_expense"
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    xp_reward = Column(Integer, default=0, nullable=False)
    criteria = Column(JSON, nullable=True) # Lógica para desbloqueo

    # Relaciones
    usuarios_con_logro = relationship("UserAchievement", back_populates="definition")

class UserAchievement(Base, AuditMixin):
    """
    Relación de logros desbloqueados por cada usuario.
    """
    __tablename__ = "user_achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(String, ForeignKey("usuarios.id"), nullable=False, index=True)
    achievement_code = Column(String, ForeignKey("achievement_definitions.code"), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    definition = relationship("AchievementDefinition", back_populates="usuarios_con_logro")
    usuario = relationship("Usuario", back_populates="logros")
