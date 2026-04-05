# src/services/dashboard.py
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal

from src.models.user import Usuario, CuentaFinanciera
from src.models.goal import MetaFinanciera
from src.models.investment import InstrumentoCatalogo

def get_dashboard_summary(db: Session, tenant_id: UUID, user_id: str):
    """
    Recopila y calcula los datos clave para la pantalla principal del usuario.
    """
    # 1. Obtener datos del perfil del usuario (Score y Flujo)
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    score = usuario.score_resiliencia if usuario else 0
    flujo = usuario.flujo_caja_libre_mensual if usuario else Decimal('0.0')

    # 2. Calcular Saldo Total (Suma de todas sus cuentas financieras)
    cuentas = db.query(CuentaFinanciera).filter(CuentaFinanciera.tenant_id == tenant_id).all()
    saldo_total = sum((c.saldo_actual for c in cuentas), Decimal('0.0'))

    # 3. Obtener la meta más próxima a vencer
    meta_proxima = db.query(MetaFinanciera).filter(
        MetaFinanciera.tenant_id == tenant_id
    ).order_by(MetaFinanciera.fecha_limite.asc()).first()

    # 4. Obtener la MEJOR oportunidad de inversión (Tier S) para su perfil actual
    mejor_oportunidad = db.query(InstrumentoCatalogo)\
        .filter(InstrumentoCatalogo.monto_minimo_apertura <= flujo)\
        .filter(InstrumentoCatalogo.score_minimo_requerido <= score)\
        .order_by(InstrumentoCatalogo.tasa_rendimiento_actual.desc())\
        .first()

    return {
        "saldo_total": saldo_total,
        "flujo_caja_mensual": flujo,
        "score_resiliencia": score,
        "meta_proxima": meta_proxima,
        "mejor_oportunidad": mejor_oportunidad
    }