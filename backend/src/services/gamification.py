from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.gamification import (
    PerfilGamificacion,
    EventoGamificacion,
    DefinicionLogro,
    LogroUsuario
)
from src.models.user import Usuario

# --- CONFIGURACIÓN DE NIVELES (MVP) ---
NIVELES = [
    {"name": "bronze", "min_xp": 0},
    {"name": "silver", "min_xp": 100},
    {"name": "gold", "min_xp": 300},
    {"name": "platinum", "min_xp": 700},
    {"name": "mythic", "min_xp": 1500},
]

def get_profile(db: Session, user_id: str) -> PerfilGamificacion:
    """Obtiene o crea el perfil de gamificación de un usuario."""
    perfil = db.query(PerfilGamificacion).filter(PerfilGamificacion.usuario_id == user_id).first()
    if not perfil:
        perfil = PerfilGamificacion(usuario_id=user_id)
        db.add(perfil)
        db.commit()
        db.refresh(perfil)
    return perfil

def award_xp(db: Session, user_id: str, amount: int, event_type: str, reference_id: Optional[str] = None):
    """Otorga XP a un usuario e incrementa su nivel si es necesario."""
    # 1. Verificar idempotencia si hay reference_id
    if reference_id:
        evento_existente = db.query(EventoGamificacion).filter(
            EventoGamificacion.usuario_id == user_id,
            EventoGamificacion.tipo_evento == event_type,
            EventoGamificacion.referencia_id == reference_id
        ).first()
        if evento_existente:
            return None # Ya se otorgó XP por este evento

    # 2. Obtener perfil
    perfil = get_profile(db, user_id)

    # 3. Registrar evento
    evento = EventoGamificacion(
        usuario_id=user_id,
        tipo_evento=event_type,
        xp_otorgado=amount,
        referencia_id=reference_id
    )
    db.add(evento)

    # 4. Actualizar XP total
    perfil.total_xp += amount

    # 5. Recalcular nivel
    nuevo_nivel = "bronze"
    for nivel in NIVELES:
        if perfil.total_xp >= nivel["min_xp"]:
            nuevo_nivel = nivel["name"]

    perfil.nivel_actual = nuevo_nivel

    db.commit()
    db.refresh(perfil)

    # 6. Evaluar logros después de ganar XP
    check_achievements(db, user_id)

    return perfil

def update_streak(db: Session, user_id: str):
    """Actualiza la racha diaria del usuario."""
    perfil = get_profile(db, user_id)
    hoy = date.today()

    if perfil.fecha_ultima_actividad == hoy:
        return perfil # Ya registrado hoy

    from datetime import timedelta
    ayer = hoy - timedelta(days=1)

    if perfil.fecha_ultima_actividad == ayer:
        perfil.racha_actual += 1
    else:
        perfil.racha_actual = 1

    perfil.fecha_ultima_actividad = hoy
    if perfil.racha_actual > perfil.racha_maxima:
        perfil.racha_maxima = perfil.racha_actual

    db.commit()
    db.refresh(perfil)

    # Al completar racha, otorgar XP por "check-in"
    award_xp(db, user_id, amount=5, event_type="daily_checkin", reference_id=str(hoy))

    # Verificar logros de racha
    check_achievements(db, user_id)

    return perfil

def check_achievements(db: Session, user_id: str):
    """Verifica si el usuario ha desbloqueado nuevos logros."""
    perfil = get_profile(db, user_id)

    # 1. Obtener logros ya desbloqueados
    codigos_desbloqueados = [lu.codigo_logro for lu in db.query(LogroUsuario).filter(LogroUsuario.usuario_id == user_id).all()]

    # 2. Definir lógica de evaluación rápida (MVP)
    logros_potenciales = [
        {"code": "first_expense", "condition": lambda p, db: db.query(func.count(EventoGamificacion.id)).filter(EventoGamificacion.usuario_id == user_id, EventoGamificacion.tipo_evento.in_(["expense_created", "audio_log", "image_log"])).scalar() >= 1},
        {"code": "streak_3", "condition": lambda p, db: p.racha_maxima >= 3},
        {"code": "streak_7", "condition": lambda p, db: p.racha_maxima >= 7},
        {"code": "silver_tier", "condition": lambda p, db: p.total_xp >= 100},
    ]

    for logro in logros_potenciales:
        if logro["code"] not in codigos_desbloqueados:
            if logro["condition"](perfil, db):
                unlock_achievement(db, user_id, logro["code"])

def unlock_achievement(db: Session, user_id: str, code: str):
    """Registra el desbloqueo de un logro y otorga su recompensa."""
    definicion = db.query(DefinicionLogro).filter(DefinicionLogro.codigo == code).first()
    if not definicion:
        return # Definición no encontrada

    nuevo_logro = LogroUsuario(
        usuario_id=user_id,
        codigo_logro=code
    )
    db.add(nuevo_logro)
    db.commit()

    # Otorga recompensa
    award_xp(db, user_id, amount=definicion.xp_recompensa, event_type="achievement_unlock", reference_id=code)

def get_next_milestone(db: Session, user_id: str):
    """Determina el siguiente paso lógico para el usuario."""
    perfil = get_profile(db, user_id)

    # Lógica de hito MVP
    if perfil.total_xp < 100:
        objetivo = 100
        progreso = (perfil.total_xp / objetivo) * 100
        return {
            "mensaje": f"Te faltan {objetivo - perfil.total_xp} XP para llegar a Silver",
            "xp_objetivo": objetivo,
            "progreso": min(progreso, 100),
            "completado": False
        }
    elif perfil.total_xp < 300:
        objetivo = 300
        progreso = ((perfil.total_xp - 100) / (objetivo - 100)) * 100
        return {
            "mensaje": f"Te faltan {objetivo - perfil.total_xp} XP para llegar a Gold",
            "xp_objetivo": objetivo,
            "progreso": min(progreso, 100),
            "completado": False
        }

    return {
        "mensaje": "¡Eres un maestro de las finanzas!",
        "xp_objetivo": None,
        "progreso": 100.0,
        "completado": True
    }

def get_calculated_profile(db: Session, user_id: str):
    """Obtiene el perfil con campos calculados para la respuesta API."""
    perfil = get_profile(db, user_id)

    # Encontrar el siguiente nivel
    siguiente_nivel = None
    xp_para_siguiente = None
    progreso = 100.0

    for i, nivel in enumerate(NIVELES):
        if perfil.total_xp < nivel["min_xp"]:
            siguiente_nivel = nivel["name"]
            umbral_anterior = NIVELES[i-1]["min_xp"] if i > 0 else 0
            xp_para_siguiente = nivel["min_xp"] - perfil.total_xp
            total_necesario_en_nivel = nivel["min_xp"] - umbral_anterior
            xp_ganado_en_nivel = perfil.total_xp - umbral_anterior
            progreso = (xp_ganado_en_nivel / total_necesario_en_nivel) * 100
            break

    return {
        "usuario_id": perfil.usuario_id,
        "total_xp": perfil.total_xp,
        "nivel_actual": perfil.nivel_actual,
        "racha_actual": perfil.racha_actual,
        "racha_maxima": perfil.racha_maxima,
        "fecha_ultima_actividad": perfil.fecha_ultima_actividad,
        "siguiente_nivel": siguiente_nivel,
        "xp_para_siguiente_nivel": xp_para_siguiente,
        "porcentaje_progreso": round(progreso, 2)
    }
