# src/services/investment.py
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal

from src.models.transaction import Transaccion
from src.models.investment import InstrumentoCatalogo, PortafolioInversion
from src.models.user import Usuario
from src.schemas.investment import PortafolioInversionCreate
 
# --- TIER LIST (Recomendaciones) ---

def generar_tierlist_dinamica(db: Session, user_id: str, tenant_id: UUID):
    """Calcula el flujo de caja, actualiza el score y retorna los instrumentos desbloqueados."""
    transacciones = db.query(Transaccion).filter(Transaccion.tenant_id == tenant_id).all()
    
    flujo_caja = Decimal('0.0')
    for t in transacciones:
        if t.sub_categoria_id == 1:
            flujo_caja += t.monto
        else:
            flujo_caja -= t.monto
            
    score_base = 500
    if flujo_caja > 0:
        puntos_extra = int(flujo_caja / 10)
        score_base = min(score_base + puntos_extra, 850)
    else:
        score_base = max(score_base - 50, 300)

    db_user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if db_user:
        db_user.flujo_caja_libre_mensual = flujo_caja
        db_user.score_resiliencia = score_base
        db.commit()

    instrumentos_desbloqueados = db.query(InstrumentoCatalogo)\
        .filter(InstrumentoCatalogo.monto_minimo_apertura <= flujo_caja)\
        .filter(InstrumentoCatalogo.score_minimo_requerido <= score_base)\
        .order_by(InstrumentoCatalogo.tasa_rendimiento_actual.desc())\
        .all()
        
    return {
        "flujo_caja_libre": flujo_caja,
        "score_resiliencia": score_base,
        "oportunidades_inversion": instrumentos_desbloqueados
    }

# --- PORTAFOLIO DE INVERSIÓN (Mis inversiones reales) ---

def create_inversion(db: Session, inversion: PortafolioInversionCreate):
    """Registra una nueva inversión realizada por el usuario."""
    db_inversion = PortafolioInversion(**inversion.model_dump())
    db.add(db_inversion)
    db.commit()
    db.refresh(db_inversion)
    return db_inversion

def get_portafolio_usuario(db: Session, tenant_id: UUID):
    """Obtiene todas las inversiones activas de un usuario."""
    return db.query(PortafolioInversion).filter(PortafolioInversion.tenant_id == tenant_id).all()