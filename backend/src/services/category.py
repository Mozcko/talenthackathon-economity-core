# src/services/category.py
from typing import Optional
from sqlalchemy.orm import Session
from src.models.transaction import Categoria, SubCategoria


def resolve_sub_categoria_id(db: Session, categoria_sugerida: str, es_ingreso: bool) -> Optional[int]:
    """
    Map the AI-suggested category string to a real sub_categoria id.
    Respects income vs expense so a gasto never maps to an Ingreso row.
    """
    tipo_flujo = "Ingreso" if es_ingreso else "Egreso"

    # 1. Partial name match within the correct flow type
    sub_cat = (
        db.query(SubCategoria)
        .join(Categoria, SubCategoria.categoria_id == Categoria.id)
        .filter(
            Categoria.tipo_flujo == tipo_flujo,
            SubCategoria.nombre.ilike(f"%{categoria_sugerida}%"),
        )
        .first()
    )

    # 2. Fallback: first sub_categoria of the correct flow type
    if not sub_cat:
        sub_cat = (
            db.query(SubCategoria)
            .join(Categoria, SubCategoria.categoria_id == Categoria.id)
            .filter(Categoria.tipo_flujo == tipo_flujo)
            .first()
        )

    return sub_cat.id if sub_cat else None

def get_catalogo_completo(db: Session):
    """
    Obtiene todas las categorías y agrupa sus subcategorías correspondientes.
    Devuelve una lista de diccionarios lista para ser parseada por Pydantic.
    """
    categorias_db = db.query(Categoria).all()
    subcategorias_db = db.query(SubCategoria).all()
    
    resultado = []
    for cat in categorias_db:
        # Filtramos las subcategorías que pertenecen a esta categoría
        subs = [s for s in subcategorias_db if s.categoria_id == cat.id]
        
        resultado.append({
            "id": cat.id,
            "nombre": cat.nombre,
            "tipo_flujo": cat.tipo_flujo,
            "subcategorias": subs
        })
        
    return resultado