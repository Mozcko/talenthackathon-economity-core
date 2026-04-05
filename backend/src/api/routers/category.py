# src/api/routers/category.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from src.core.database import get_db
from src.core.security import get_current_user_token
from src.schemas.category import CategoriaResponse
from src.services import category as category_service

router = APIRouter(prefix="/categorias", tags=["Catálogos"])

@router.get("/", response_model=List[CategoriaResponse])
def obtener_catalogo_categorias(
    db: Session = Depends(get_db),
    token_payload: Dict[str, Any] = Depends(get_current_user_token)
):
    """
    Obtiene el catálogo completo de categorías y subcategorías.
    Requiere un usuario autenticado.
    """
    # Al ser un catálogo general, no filtramos por tenant_id, 
    # pero sí exigimos que el token sea válido.
    return category_service.get_catalogo_completo(db)