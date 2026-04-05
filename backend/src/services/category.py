# src/services/category.py
from sqlalchemy.orm import Session
from src.models.transaction import Categoria, SubCategoria

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