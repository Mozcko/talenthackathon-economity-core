"""
Pruebas unitarias para src/services/category.py
"""
import pytest
from unittest.mock import MagicMock

import src.services.category as svc


def _make_categoria(id: int, nombre: str, tipo_flujo: str) -> MagicMock:
    cat = MagicMock()
    cat.id = id
    cat.nombre = nombre
    cat.tipo_flujo = tipo_flujo
    return cat


def _make_subcategoria(categoria_id: int, nombre: str) -> MagicMock:
    sub = MagicMock()
    sub.categoria_id = categoria_id
    sub.nombre = nombre
    return sub


class TestGetCatalogoCompleto:
    def test_agrupa_subcategorias_bajo_su_categoria(self, mock_db):
        cat1 = _make_categoria(1, "Ingresos", "entrada")
        cat2 = _make_categoria(2, "Gastos", "salida")
        sub1 = _make_subcategoria(1, "Salario")
        sub2 = _make_subcategoria(1, "Freelance")
        sub3 = _make_subcategoria(2, "Renta")

        # Primera llamada a query().all() → categorías, segunda → subcategorías
        mock_db.query.return_value.all.side_effect = [
            [cat1, cat2],
            [sub1, sub2, sub3],
        ]

        resultado = svc.get_catalogo_completo(mock_db)

        assert len(resultado) == 2

        cat_ingresos = next(r for r in resultado if r["id"] == 1)
        assert cat_ingresos["nombre"] == "Ingresos"
        assert cat_ingresos["tipo_flujo"] == "entrada"
        assert len(cat_ingresos["subcategorias"]) == 2

        cat_gastos = next(r for r in resultado if r["id"] == 2)
        assert len(cat_gastos["subcategorias"]) == 1
        assert cat_gastos["subcategorias"][0].nombre == "Renta"

    def test_retorna_lista_vacia_sin_categorias(self, mock_db):
        mock_db.query.return_value.all.side_effect = [[], []]

        resultado = svc.get_catalogo_completo(mock_db)

        assert resultado == []

    def test_categoria_sin_subcategorias_tiene_lista_vacia(self, mock_db):
        cat = _make_categoria(1, "Sin hijos", "salida")
        mock_db.query.return_value.all.side_effect = [[cat], []]

        resultado = svc.get_catalogo_completo(mock_db)

        assert resultado[0]["subcategorias"] == []

    def test_estructura_de_cada_entrada(self, mock_db):
        cat = _make_categoria(99, "Test", "entrada")
        mock_db.query.return_value.all.side_effect = [[cat], []]

        resultado = svc.get_catalogo_completo(mock_db)

        entrada = resultado[0]
        assert "id" in entrada
        assert "nombre" in entrada
        assert "tipo_flujo" in entrada
        assert "subcategorias" in entrada
