# src/services/goal.py
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal

from src.models.goal import MetaFinanciera
from src.schemas.goal import MetaFinancieraCreate

def create_meta(db: Session, meta: MetaFinancieraCreate):
    """Crea una nueva meta financiera en la base de datos."""
    db_meta = MetaFinanciera(**meta.model_dump())
    db.add(db_meta)
    db.commit()
    db.refresh(db_meta)
    return db_meta

def get_metas_by_usuario(db: Session, tenant_id: UUID):
    """Obtiene todas las metas que le pertenecen a un usuario/tenant específico."""
    return db.query(MetaFinanciera).filter(MetaFinanciera.tenant_id == tenant_id).all()

def add_progreso_meta(db: Session, meta_id: UUID, monto: Decimal, tenant_id: UUID):
    """Suma un monto específico al progreso de una meta, validando que le pertenezca al usuario."""
    db_meta = db.query(MetaFinanciera).filter(
        MetaFinanciera.id == meta_id, 
        MetaFinanciera.tenant_id == tenant_id
    ).first()
    
    if db_meta:
        # Sumamos el monto de forma segura con Decimal
        db_meta.progreso_actual += monto
        db.commit()
        db.refresh(db_meta)
        
    return db_meta

def delete_meta(db: Session, meta_id: UUID, tenant_id: UUID) -> bool:
    """Elimina una meta financiera si le pertenece al usuario."""
    db_meta = db.query(MetaFinanciera).filter(
        MetaFinanciera.id == meta_id, 
        MetaFinanciera.tenant_id == tenant_id
    ).first()
    
    if db_meta:
        db.delete(db_meta)
        db.commit()
        return True
    return False