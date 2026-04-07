from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.gamification import (
    UserGamificationProfile, 
    GamificationEvent, 
    AchievementDefinition, 
    UserAchievement
)
from src.models.user import Usuario

# --- CONFIGURACIÓN DE NIVELES (MVP) ---
TIERS = [
    {"name": "bronze", "min_xp": 0},
    {"name": "silver", "min_xp": 100},
    {"name": "gold", "min_xp": 300},
    {"name": "platinum", "min_xp": 700},
    {"name": "mythic", "min_xp": 1500},
]

def get_profile(db: Session, user_id: str) -> UserGamificationProfile:
    """Obtiene o crea el perfil de gamificación de un usuario."""
    profile = db.query(UserGamificationProfile).filter(UserGamificationProfile.user_id == user_id).first()
    if not profile:
        profile = UserGamificationProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

def award_xp(db: Session, user_id: str, amount: int, event_type: str, reference_id: Optional[str] = None):
    """Otorga XP a un usuario e incrementa su nivel si es necesario."""
    # 1. Verificar idempotencia si hay reference_id
    if reference_id:
        existing_event = db.query(GamificationEvent).filter(
            GamificationEvent.user_id == user_id,
            GamificationEvent.event_type == event_type,
            GamificationEvent.reference_id == reference_id
        ).first()
        if existing_event:
            return None # Ya se otorgó XP por este evento

    # 2. Obtener perfil
    profile = get_profile(db, user_id)
    
    # 3. Registrar evento
    event = GamificationEvent(
        user_id=user_id,
        event_type=event_type,
        xp_awarded=amount,
        reference_id=reference_id
    )
    db.add(event)
    
    # 4. Actualizar XP total
    profile.total_xp += amount
    
    # 5. Recalcular Tier
    new_tier = "bronze"
    for tier in TIERS:
        if profile.total_xp >= tier["min_xp"]:
            new_tier = tier["name"]
    
    profile.current_tier = new_tier
    
    db.commit()
    db.refresh(profile)
    
    # 6. Evaluar logros después de ganar XP
    check_achievements(db, user_id)
    
    return profile

def update_streak(db: Session, user_id: str):
    """Actualiza la racha diaria del usuario."""
    profile = get_profile(db, user_id)
    today = date.today()
    
    if profile.last_activity_date == today:
        return profile # Ya registrado hoy
    
    yesterday = today.replace(day=today.day - 1) # Simplificación (cuidado con fin de mes)
    # Mejor usar timedelta:
    from datetime import timedelta
    yesterday = today - timedelta(days=1)
    
    if profile.last_activity_date == yesterday:
        profile.current_streak += 1
    else:
        profile.current_streak = 1
        
    profile.last_activity_date = today
    if profile.current_streak > profile.max_streak:
        profile.max_streak = profile.current_streak
        
    db.commit()
    db.refresh(profile)
    
    # Al completar racha, otorgar XP por "check-in"
    award_xp(db, user_id, amount=5, event_type="daily_checkin", reference_id=str(today))
    
    # Check for streak achievements
    check_achievements(db, user_id)
    
    return profile

def check_achievements(db: Session, user_id: str):
    """Verifica si el usuario ha desbloqueado nuevos logros."""
    profile = get_profile(db, user_id)
    
    # 1. Obtener logros ya desbloqueados
    unlocked_codes = [ua.achievement_code for ua in db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()]
    
    # 2. Definir lógica de evaluación rápida (MVP)
    potential_achievements = [
        {"code": "first_expense", "condition": lambda p, db: db.query(func.count(GamificationEvent.id)).filter(GamificationEvent.user_id == user_id, GamificationEvent.event_type.in_(["expense_created", "audio_log", "image_log"])).scalar() >= 1},
        {"code": "streak_3", "condition": lambda p, db: p.max_streak >= 3},
        {"code": "streak_7", "condition": lambda p, db: p.max_streak >= 7},
        {"code": "silver_tier", "condition": lambda p, db: p.total_xp >= 100},
    ]
    
    for ach in potential_achievements:
        if ach["code"] not in unlocked_codes:
            if ach["condition"](profile, db):
                unlock_achievement(db, user_id, ach["code"])

def unlock_achievement(db: Session, user_id: str, code: str):
    """Registra el desbloqueo de un logro y otorga su recompensa."""
    definition = db.query(AchievementDefinition).filter(AchievementDefinition.code == code).first()
    if not definition:
        return # Definición no encontrada
        
    new_unlock = UserAchievement(
        user_id=user_id,
        achievement_code=code
    )
    db.add(new_unlock)
    db.commit()
    
    # Otorga recompensa
    award_xp(db, user_id, amount=definition.xp_reward, event_type="achievement_unlock", reference_id=code)

def get_next_milestone(db: Session, user_id: str):
    """Determina el siguiente paso lógico para el usuario."""
    profile = get_profile(db, user_id)
    
    # Lógica de Milestone MVP
    if profile.total_xp < 100:
        target = 100
        progress = (profile.total_xp / target) * 100
        return {
            "message": f"Te faltan {target - profile.total_xp} XP para llegar a Silver",
            "target_xp": target,
            "progress": min(progress, 100),
            "is_completed": False
        }
    elif profile.total_xp < 300:
        target = 300
        progress = ((profile.total_xp - 100) / (target - 100)) * 100
        return {
            "message": f"Te faltan {target - profile.total_xp} XP para llegar a Gold",
            "target_xp": target,
            "progress": min(progress, 100),
            "is_completed": False
        }
    
    return {
        "message": "¡Eres un maestro de las finanzas!",
        "target_xp": None,
        "progress": 100.0,
        "is_completed": True
    }

def get_calculated_profile(db: Session, user_id: str):
    """Obtiene el perfil con campos calculados para la respuesta API."""
    profile = get_profile(db, user_id)
    
    # Encontrar el siguiente nivel
    next_tier = None
    xp_to_next = None
    progress = 100.0
    
    for i, tier in enumerate(TIERS):
        if profile.total_xp < tier["min_xp"]:
            next_tier = tier["name"]
            prev_threshold = TIERS[i-1]["min_xp"] if i > 0 else 0
            xp_to_next = tier["min_xp"] - profile.total_xp
            total_needed_in_tier = tier["min_xp"] - prev_threshold
            xp_gained_in_tier = profile.total_xp - prev_threshold
            progress = (xp_gained_in_tier / total_needed_in_tier) * 100
            break
            
    return {
        "user_id": profile.user_id,
        "total_xp": profile.total_xp,
        "current_tier": profile.current_tier,
        "current_streak": profile.current_streak,
        "max_streak": profile.max_streak,
        "last_activity_date": profile.last_activity_date,
        "next_tier": next_tier,
        "xp_to_next_tier": xp_to_next,
        "progress_percentage": round(progress, 2)
    }
