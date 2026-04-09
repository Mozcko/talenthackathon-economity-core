"""
Pruebas unitarias para src/services/dashboard.py
"""
import pytest
from unittest.mock import MagicMock, call
from uuid import uuid4
from decimal import Decimal

import src.services.dashboard as svc


class TestGetDashboardSummary:
    def _setup_db(self, mock_db, usuario=None, saldo_transacciones=None, meta=None, oportunidad=None):
        """Configura el mock_db con returns encadenados para cada query."""
        q = mock_db.query.return_value
        # Usuario → primera llamada a filter().first()
        q.filter.return_value.first.side_effect = [usuario, meta, oportunidad]
        # Saldo total desde transacciones → filter().scalar()
        q.filter.return_value.scalar.return_value = saldo_transacciones
        # Oportunidad: filter().filter().order_by().first()
        q.filter.return_value.filter.return_value.order_by.return_value.first.return_value = oportunidad
        # Meta: filter().order_by().first()
        q.filter.return_value.order_by.return_value.first.return_value = meta

    def test_retorna_claves_esperadas(self, mock_db):
        usuario = MagicMock()
        usuario.score_resiliencia = 600
        usuario.flujo_caja_libre_mensual = Decimal("1000")

        self._setup_db(mock_db, usuario=usuario)

        resultado = svc.get_dashboard_summary(mock_db, uuid4(), "user_1")

        assert "saldo_total" in resultado
        assert "flujo_caja_mensual" in resultado
        assert "score_resiliencia" in resultado
        assert "meta_proxima" in resultado
        assert "mejor_oportunidad" in resultado

    def test_score_y_flujo_del_usuario(self, mock_db):
        usuario = MagicMock()
        usuario.score_resiliencia = 720
        usuario.flujo_caja_libre_mensual = Decimal("2500")

        self._setup_db(mock_db, usuario=usuario)

        resultado = svc.get_dashboard_summary(mock_db, uuid4(), "user_1")

        assert resultado["score_resiliencia"] == 720
        assert resultado["flujo_caja_mensual"] == Decimal("2500")

    def test_score_y_flujo_por_defecto_si_usuario_no_existe(self, mock_db):
        self._setup_db(mock_db, usuario=None, saldo_transacciones=None)

        resultado = svc.get_dashboard_summary(mock_db, uuid4(), "user_inexistente")

        assert resultado["score_resiliencia"] == 0
        assert resultado["flujo_caja_mensual"] == Decimal("0.0")

    def test_saldo_total_es_suma_de_transacciones(self, mock_db):
        usuario = MagicMock()
        usuario.score_resiliencia = 500
        usuario.flujo_caja_libre_mensual = Decimal("0")

        self._setup_db(mock_db, usuario=usuario, saldo_transacciones=Decimal("1750"))

        resultado = svc.get_dashboard_summary(mock_db, uuid4(), "user_1")

        assert resultado["saldo_total"] == Decimal("1750")

    def test_saldo_total_es_cero_sin_transacciones(self, mock_db):
        usuario = MagicMock()
        usuario.score_resiliencia = 500
        usuario.flujo_caja_libre_mensual = Decimal("0")

        self._setup_db(mock_db, usuario=usuario, saldo_transacciones=None)

        resultado = svc.get_dashboard_summary(mock_db, uuid4(), "user_1")

        assert resultado["saldo_total"] == Decimal("0.0")
