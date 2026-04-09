# seed.py
from sqlalchemy.orm import Session
from src.core.database import SessionLocal, engine
from src.models.base import Base
from src.models.transaction import Categoria, SubCategoria
from src.models.investment import InstrumentoCatalogo

def seed_database():
    # 1. Asegurar que las tablas existan
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # --- SEED DE CATEGORÍAS Y SUBCATEGORÍAS ---
        if not db.query(Categoria).first():
            print("🌱 Sembrando Categorías Conductuales...")
            cat_ingreso = Categoria(nombre="Ingresos", tipo_flujo="Ingreso")
            cat_esencial = Categoria(nombre="Supervivencia (Esenciales)", tipo_flujo="Egreso")
            cat_crecimiento = Categoria(nombre="Crecimiento y Salud", tipo_flujo="Egreso")
            cat_riesgo = Categoria(nombre="Dopamina y Riesgo (Peligro)", tipo_flujo="Egreso")
            db.add_all([cat_ingreso, cat_esencial, cat_crecimiento, cat_riesgo])
            db.commit()

            # SUBCATEGORÍAS
            subs = [
                # Ingresos
                SubCategoria(categoria_id=cat_ingreso.id, nombre="Sueldo/Nómina"),
                SubCategoria(categoria_id=cat_ingreso.id, nombre="Ventas/Freelance"),
                
                # Esenciales (Bajo Riesgo)
                SubCategoria(categoria_id=cat_esencial.id, nombre="Renta/Vivienda", is_risky=False, risk_level="low"),
                SubCategoria(categoria_id=cat_esencial.id, nombre="Despensa/Super", is_risky=False, risk_level="low"),
                SubCategoria(categoria_id=cat_esencial.id, nombre="Servicios (Luz/Agua)", is_risky=False, risk_level="low"),
                
                # Crecimiento (Bajo Riesgo)
                SubCategoria(categoria_id=cat_crecimiento.id, nombre="Educación/Cursos", is_risky=False, risk_level="low"),
                SubCategoria(categoria_id=cat_crecimiento.id, nombre="Terapia/Salud", is_risky=False, risk_level="low"),
                SubCategoria(categoria_id=cat_crecimiento.id, nombre="Libros", is_risky=False, risk_level="low"),

                # Riesgo (Medio/Alto)
                SubCategoria(categoria_id=cat_riesgo.id, nombre="Apuestas/Casino", is_risky=True, risk_level="high"),
                SubCategoria(categoria_id=cat_riesgo.id, nombre="Microtransacciones/Juegos", is_risky=True, risk_level="medium"),
                SubCategoria(categoria_id=cat_riesgo.id, nombre="Antros/Fiesta", is_risky=True, risk_level="medium"),
                SubCategoria(categoria_id=cat_riesgo.id, nombre="Suscripciones Olvidadas", is_risky=True, risk_level="low"),
            ]
            db.add_all(subs)
            db.commit()

        # --- SEED DE CATÁLOGO DE INVERSIONES (Mismo de antes, pero con nombres en español) ---
        if not db.query(InstrumentoCatalogo).first():
            # ... (se mantiene igual o se ajusta si es necesario)
            pass

        # --- SEED DE GAMIFICACIÓN ---
        from src.models.gamification import DefinicionLogro
        if not db.query(DefinicionLogro).first():
            print("🏆 Sembrando Logros Conductuales...")
            achievements = [
                DefinicionLogro(
                    codigo="first_expense", nombre="Primer Paso", 
                    descripcion="Registraste tu primer movimiento. El camino a la disciplina comienza aquí.", 
                    xp_recompensa=50
                ),
                DefinicionLogro(
                    codigo="streak_3", nombre="Racha de 3", 
                    descripcion="Tres días seguidos. Casi pareces una persona responsable.", 
                    xp_recompensa=100
                ),
                DefinicionLogro(
                    codigo="streak_7", nombre="Semana Perfecta", 
                    descripcion="Siete días de control total. Tu coach está... ¿orgulloso?", 
                    xp_recompensa=250
                ),
                DefinicionLogro(
                    codigo="first_risky_logged", nombre="Honestidad Brutal", 
                    descripcion="Registraste un gasto riesgoso. Admitirlo es el primer paso.", 
                    xp_recompensa=75
                ),
                DefinicionLogro(
                    codigo="silver_tier", nombre="Ascenso a Plata", 
                    descripcion="Nivel Plata. Ya no eres un novato total.", 
                    xp_recompensa=150
                ),
            ]
            db.add_all(achievements)
            db.commit()

        print("✅ Base de datos poblada exitosamente con datos Mock.")
        
    except Exception as e:
        print(f"❌ Error durante el seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()