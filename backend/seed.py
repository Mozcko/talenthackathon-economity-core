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
        # Verificamos si ya existen para no duplicar
        if not db.query(Categoria).first():
            print("🌱 Sembrando Categorías...")
            cat_ingreso = Categoria(nombre="Ingresos", tipo_flujo="Ingreso")
            cat_gasto = Categoria(nombre="Gastos Corrientes", tipo_flujo="Egreso")
            db.add_all([cat_ingreso, cat_gasto])
            db.commit()

            # SUBCATEGORÍAS (Los IDs 1, 2, 3, 4 coinciden con tu Prompt de LangChain)
            sub1 = SubCategoria(id=1, categoria_id=cat_ingreso.id, nombre="Ingresos Generales")
            sub2 = SubCategoria(id=2, categoria_id=cat_gasto.id, nombre="Comida/Despensa")
            sub3 = SubCategoria(id=3, categoria_id=cat_gasto.id, nombre="Transporte/Gasolina")
            sub4 = SubCategoria(id=4, categoria_id=cat_gasto.id, nombre="Otros Gastos")
            db.add_all([sub1, sub2, sub3, sub4])
            db.commit()

        # --- SEED DE CATÁLOGO DE INVERSIONES ---
        if not db.query(InstrumentoCatalogo).first():
            print("📈 Sembrando Catálogo de Inversiones (Tier List)...")
            instrumentos = [
                InstrumentoCatalogo(
                    tipo="CETES", entidad="CetesDirecto", 
                    tasa_rendimiento_actual=0.1050, monto_minimo_apertura=100.00, 
                    score_minimo_requerido=300, beneficio_fiscal=False
                ),
                InstrumentoCatalogo(
                    tipo="SOFIPO", entidad="Nu México", 
                    tasa_rendimiento_actual=0.1425, monto_minimo_apertura=1.00, 
                    score_minimo_requerido=400, beneficio_fiscal=True
                ),
                InstrumentoCatalogo(
                    tipo="SOFIPO", entidad="Klar", 
                    tasa_rendimiento_actual=0.1600, monto_minimo_apertura=100.00, 
                    score_minimo_requerido=550, beneficio_fiscal=True
                ),
                InstrumentoCatalogo(
                    tipo="SOFIPO", entidad="Finsus", 
                    tasa_rendimiento_actual=0.1501, monto_minimo_apertura=100.00, 
                    score_minimo_requerido=600, beneficio_fiscal=True
                ),
            ]
            db.add_all(instrumentos)
            db.commit()
            
        # --- SEED DE GAMIFICACIÓN ---
        from src.models.gamification import AchievementDefinition
        if not db.query(AchievementDefinition).first():
            print("🏆 Sembrando Logros de Gamificación...")
            achievements = [
                AchievementDefinition(
                    code="first_expense", name="Primer Gasto", 
                    description="Registraste tu primer gasto en la plataforma.", 
                    xp_reward=50
                ),
                AchievementDefinition(
                    code="streak_3", name="Trifecta", 
                    description="Mantuviste una racha de 3 días registrando actividad.", 
                    xp_reward=100
                ),
                AchievementDefinition(
                    code="streak_7", name="Semana Perfecta", 
                    description="Mantuviste una racha de 7 días. ¡Excelente disciplina!", 
                    xp_reward=250
                ),
                AchievementDefinition(
                    code="silver_tier", name="Ascenso a Plata", 
                    description="Alcanzaste el nivel Plata acumulando 100 XP.", 
                    xp_reward=150
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