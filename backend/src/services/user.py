# src/services/user.py
from sqlalchemy.orm import Session
from src.models.user import Usuario, CuentaFinanciera
from src.schemas.user import UsuarioCreate, CuentaFinancieraCreate

# --- SERVICIOS DE USUARIO ---

def create_usuario(db: Session, user: UsuarioCreate):
    """Crea un nuevo usuario en la base de datos."""
    # Convertimos el esquema Pydantic a un modelo SQLAlchemy
    db_user = Usuario(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # Actualizamos la variable con los datos generados (ej. created_at)
    return db_user
 
def get_usuario(db: Session, user_id: str):
    """Obtiene un usuario por su ID."""
    return db.query(Usuario).filter(Usuario.id == user_id).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene una lista paginada de usuarios."""
    return db.query(Usuario).offset(skip).limit(limit).all()

# --- SERVICIOS DE CUENTA FINANCIERA ---

def create_cuenta_financiera(db: Session, cuenta: CuentaFinancieraCreate):
    """Crea una nueva cuenta financiera para un usuario."""
    db_cuenta = CuentaFinanciera(**cuenta.model_dump())
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta

def get_cuentas_by_usuario(db: Session, user_id: str):
    """Obtiene todas las cuentas financieras de un usuario específico."""
    return db.query(CuentaFinanciera).filter(CuentaFinanciera.usuario_id == user_id).all()