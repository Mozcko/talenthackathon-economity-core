from sqlalchemy.orm import Session
from uuid import UUID

# Asumiendo la estructura convencional basada en tus otros archivos
from src.models.transaction import Transaccion
from src.schemas.transaction import TransaccionCreate

def create_transaccion(db: Session, transaccion: TransaccionCreate):
    """Persiste una nueva transacción en la base de datos y dispara eventos de gamificación."""
    db_transaccion = Transaccion(**transaccion.model_dump())
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)

    # --- Actualizar saldo de la cuenta ---
    try:
        from src.models.user import CuentaFinanciera
        cuenta_upd = db.query(CuentaFinanciera).filter(CuentaFinanciera.id == db_transaccion.cuenta_id).first()
        if cuenta_upd:
            cuenta_upd.saldo_actual = (cuenta_upd.saldo_actual or 0) + db_transaccion.monto
            db.commit()
    except Exception as e:
        print(f"⚠️ Error actualizando saldo: {e}")

    # --- Hook de Gamificación ---
    try:
        from src.models.user import CuentaFinanciera
        from src.models.transaction import SubCategoria
        from src.services import gamification as gamification_service
        
        # Obtenemos el usuario dueño de la cuenta
        cuenta = db.query(CuentaFinanciera).filter(CuentaFinanciera.id == db_transaccion.cuenta_id).first()
        if cuenta:
            # 1. Actualizar racha diaria
            gamification_service.update_streak(db, user_id=cuenta.usuario_id)
            
            # 2. Otorgar XP base por registro de gasto
            gamification_service.award_xp(
                db, 
                user_id=cuenta.usuario_id, 
                amount=10, 
                event_type="expense_created", 
                reference_id=str(db_transaccion.id)
            )

            # 3. Bono de Honestidad por gastos riesgosos
            sub_cat = db.query(SubCategoria).filter(SubCategoria.id == db_transaccion.sub_categoria_id).first()
            if sub_cat and sub_cat.is_risky:
                gamification_service.award_honesty_xp(
                    db, 
                    user_id=cuenta.usuario_id, 
                    transaction_id=str(db_transaccion.id)
                )
    except Exception as e:
        # No queremos que un error en gamificación rompa el flujo principal de transacciones
        print(f"⚠️ Error en gamificación: {e}")

    return db_transaccion

def get_transacciones_by_cuenta(db: Session, cuenta_id: UUID):
    """Obtiene el listado completo de transacciones de una cuenta financiera."""
    return db.query(Transaccion).filter(Transaccion.cuenta_id == cuenta_id).all()

