from sqlalchemy.orm import Session
from uuid import UUID

# Asumiendo la estructura convencional basada en tus otros archivos
from src.models.transaction import Transaccion
from src.schemas.transaction import TransaccionCreate

def create_transaccion(db: Session, transaccion: TransaccionCreate):
    """Persiste una nueva transacción en la base de datos."""
    db_transaccion = Transaccion(**transaccion.model_dump())
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

def get_transacciones_by_cuenta(db: Session, cuenta_id: UUID):
    """Obtiene el listado completo de transacciones de una cuenta financiera."""
    return db.query(Transaccion).filter(Transaccion.cuenta_id == cuenta_id).all()

