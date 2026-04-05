# src/schemas/category.py
from pydantic import BaseModel, ConfigDict
from typing import List

class SubCategoriaResponse(BaseModel):
    id: int
    nombre: str
    
    model_config = ConfigDict(from_attributes=True)

class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    tipo_flujo: str
    subcategorias: List[SubCategoriaResponse] = []

    model_config = ConfigDict(from_attributes=True)