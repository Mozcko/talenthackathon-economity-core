"""
Pruebas unitarias para src/services/investment.py
"""
import pytest
from unittest.mock import MagicMock, patch, call
from uuid import uuid4
from decimal import Decimal

import src.services.investment as svc


def _make_transaccion(sub_categoria_id: int, monto: Decimal) -> MagicMock:
    t = MagicMock()
    t.sub_categoria_id = sub_categoria_id
    t.monto = monto
    return t


class TestGenerarTierlistDinamica:
    def test_flujo_positivo_con_ingresos_y_gastos(self, mock_db):
        """sub_categoria_id==1 suma, cualquier otro resta."""
        transacciones = [
            _make_transaccion(1, Decimal("500")),   # ingreso +500
            _make_transaccion(2, Decimal("200")),   # gasto  -200
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = transacciones
        mock_db.query.return_value.filter.return_value.first.return_value = None  # usuario no encontrado
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []

        resultado = svc.generar_tierlist_dinamica(mock_db, "user_1", uuid4())

        assert resultado["flujo_caja_libre"] == Decimal("300")

    def test_score_sube_con_flujo_positivo(self, mock_db):
        """score = min(500 + int(flujo/10), 850)"""
        transacciones = [_make_transaccion(1, Decimal("1000"))]
        mock_db.query.return_value.filter.return_value.all.return_value = transacciones
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []

        resultado = svc.generar_tierlist_dinamica(mock_db, "user_1", uuid4())

        # 500 + int(1000/10) = 600
        assert resultado["score_resiliencia"] == 600

    def test_score_maximo_es_850(self, mock_db):
        transacciones = [_make_transaccion(1, Decimal("50000"))]
        mock_db.query.return_value.filter.return_value.all.return_value = transacciones
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []

        resultado = svc.generar_tierlist_dinamica(mock_db, "user_1", uuid4())

        assert resultado["score_resiliencia"] == 850

    def test_score_baja_con_flujo_negativo(self, mock_db):
        """score = max(500 - 50, 300) = 450"""
        transacciones = [_make_transaccion(2, Decimal("100"))]  # solo gasto
        mock_db.query.return_value.filter.return_value.all.return_value = transacciones
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []

        resultado = svc.generar_tierlist_dinamica(mock_db, "user_1", uuid4())

        assert resultado["score_resiliencia"] == 450

    def test_actualiza_usuario_cuando_existe(self, mock_db):
        transacciones = [_make_transaccion(1, Decimal("200"))]
        usuario = MagicMock()

        # Primera query devuelve transacciones, segunda el usuario
        mock_db.query.return_value.filter.return_value.all.return_value = transacciones
        mock_db.query.return_value.filter.return_value.first.return_value = usuario
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []

        svc.generar_tierlist_dinamica(mock_db, "user_1", uuid4())

        assert usuario.flujo_caja_libre_mensual == Decimal("200")
        mock_db.commit.assert_called()

    def test_retorna_claves_esperadas(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []

        resultado = svc.generar_tierlist_dinamica(mock_db, "user_1", uuid4())

        assert "flujo_caja_libre" in resultado
        assert "score_resiliencia" in resultado
        assert "oportunidades_inversion" in resultado


class TestCreateInversion:
    def test_persiste_inversion_y_la_retorna(self, mock_db):
        schema = MagicMock()
        schema.model_dump.return_value = {"usuario_id": "u1", "monto": Decimal("500")}

        with patch("src.services.investment.PortafolioInversion") as MockPortafolio:
            db_inv = MagicMock()
            MockPortafolio.return_value = db_inv

            resultado = svc.create_inversion(mock_db, schema)

            mock_db.add.assert_called_once_with(db_inv)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(db_inv)
            assert resultado is db_inv


class TestGetPortafolioUsuario:
    def test_retorna_inversiones_del_tenant(self, mock_db):
        inversiones = [MagicMock(), MagicMock()]
        mock_db.query.return_value.filter.return_value.all.return_value = inversiones

        resultado = svc.get_portafolio_usuario(mock_db, uuid4())

        assert resultado == inversiones

    def test_retorna_lista_vacia_si_no_hay_inversiones(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []

        resultado = svc.get_portafolio_usuario(mock_db, uuid4())

        assert resultado == []
