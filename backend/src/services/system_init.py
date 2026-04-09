"""
System data bootstrap — runs on every app startup (idempotent).
These are required lookup tables the app cannot function without.
This is NOT dev seed data; it belongs in production.
"""
from sqlalchemy.orm import Session
from src.core.database import SessionLocal


def initialize_system_data() -> None:
    db: Session = SessionLocal()
    try:
        _init_categories(db)
        _init_achievements(db)
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def _init_categories(db: Session) -> None:
    from src.models.transaction import Categoria, SubCategoria

    if db.query(Categoria).first():
        return  # already initialized

    cat_ingreso    = Categoria(nombre="Ingresos",                       tipo_flujo="Ingreso")
    cat_esencial   = Categoria(nombre="Supervivencia (Esenciales)",     tipo_flujo="Egreso")
    cat_crecimiento= Categoria(nombre="Crecimiento y Salud",            tipo_flujo="Egreso")
    cat_riesgo     = Categoria(nombre="Dopamina y Riesgo (Peligro)",    tipo_flujo="Egreso")
    cat_otros      = Categoria(nombre="Otros",                          tipo_flujo="Egreso")
    db.add_all([cat_ingreso, cat_esencial, cat_crecimiento, cat_riesgo, cat_otros])
    db.flush()  # get auto-incremented ids before creating children

    subs = [
        # Ingresos
        SubCategoria(categoria_id=cat_ingreso.id,     nombre="Sueldo/Nómina"),
        SubCategoria(categoria_id=cat_ingreso.id,     nombre="Ventas/Freelance"),
        # Esenciales
        SubCategoria(categoria_id=cat_esencial.id,    nombre="Renta/Vivienda",        is_risky=False, risk_level="low"),
        SubCategoria(categoria_id=cat_esencial.id,    nombre="Despensa/Super",         is_risky=False, risk_level="low"),
        SubCategoria(categoria_id=cat_esencial.id,    nombre="Servicios (Luz/Agua)",   is_risky=False, risk_level="low"),
        SubCategoria(categoria_id=cat_esencial.id,    nombre="Transporte/Gasolina",    is_risky=False, risk_level="low"),
        # Crecimiento
        SubCategoria(categoria_id=cat_crecimiento.id, nombre="Educación/Cursos",       is_risky=False, risk_level="low"),
        SubCategoria(categoria_id=cat_crecimiento.id, nombre="Terapia/Salud",          is_risky=False, risk_level="low"),
        SubCategoria(categoria_id=cat_crecimiento.id, nombre="Libros",                 is_risky=False, risk_level="low"),
        SubCategoria(categoria_id=cat_crecimiento.id, nombre="Restaurantes/Comida",    is_risky=False, risk_level="low"),
        # Riesgo
        SubCategoria(categoria_id=cat_riesgo.id,      nombre="Apuestas/Casino",        is_risky=True,  risk_level="high"),
        SubCategoria(categoria_id=cat_riesgo.id,      nombre="Microtransacciones/Juegos", is_risky=True, risk_level="medium"),
        SubCategoria(categoria_id=cat_riesgo.id,      nombre="Antros/Fiesta",          is_risky=True,  risk_level="medium"),
        SubCategoria(categoria_id=cat_riesgo.id,      nombre="Suscripciones Olvidadas",is_risky=True,  risk_level="low"),
        SubCategoria(categoria_id=cat_riesgo.id,      nombre="Alcohol",                is_risky=True,  risk_level="medium"),
        # Otros
        SubCategoria(categoria_id=cat_otros.id,       nombre="Varios/Sin categoría",   is_risky=False, risk_level="low"),
    ]
    db.add_all(subs)
    db.commit()
    print("✅ Categorías y subcategorías inicializadas.")


def _init_achievements(db: Session) -> None:
    from src.models.gamification import DefinicionLogro

    if db.query(DefinicionLogro).first():
        return  # already initialized

    achievements = [
        DefinicionLogro(codigo="first_expense",      nombre="Primer Paso",
                        descripcion="Registraste tu primer movimiento.",
                        xp_recompensa=50),
        DefinicionLogro(codigo="streak_3",           nombre="Racha de 3",
                        descripcion="Tres días seguidos de registro.",
                        xp_recompensa=100),
        DefinicionLogro(codigo="streak_7",           nombre="Semana Perfecta",
                        descripcion="Siete días de control total.",
                        xp_recompensa=250),
        DefinicionLogro(codigo="first_risky_logged", nombre="Honestidad Brutal",
                        descripcion="Registraste un gasto riesgoso. Admitirlo es el primer paso.",
                        xp_recompensa=75),
        DefinicionLogro(codigo="silver_tier",        nombre="Ascenso a Plata",
                        descripcion="Nivel Plata desbloqueado.",
                        xp_recompensa=150),
    ]
    db.add_all(achievements)
    db.commit()
    print("✅ Logros de gamificación inicializados.")
