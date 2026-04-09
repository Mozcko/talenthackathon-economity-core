"""
Pruebas unitarias para src/services/transaction.py

Nota: gamification_service y CuentaFinanciera se importan de forma lazy
dentro de create_transaccion, por lo que se parchean en su ruta de origen.
"""
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

import src.services.transaction as svc


class TestCreateTransaccion:
    def _make_schema(self):
        schema = MagicMock()
        schema.model_dump.return_value = {"monto": 100, "cuenta_id": uuid4()}
        return schema

    def test_persiste_transaccion_y_la_retorna(self, mock_db):
        schema = self._make_schema()
        mock_db.query.return_value.filter.return_value.first.return_value = None  # sin cuenta

        with patch("src.services.transaction.Transaccion") as MockTx:
            db_tx = MagicMock()
            MockTx.return_value = db_tx

            resultado = svc.create_transaccion(mock_db, schema)

            mock_db.add.assert_called_once_with(db_tx)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(db_tx)
            assert resultado is db_tx

    def test_dispara_gamificacion_cuando_existe_la_cuenta(self, mock_db):
        schema = self._make_schema()
        cuenta = MagicMock()
        cuenta.usuario_id = "user_123"
        # 1st .first() → balance update CuentaFinanciera; 2nd → gamification CuentaFinanciera; 3rd → SubCategoria (None = not risky)
        mock_db.query.return_value.filter.return_value.first.side_effect = [cuenta, cuenta, None]

        with patch("src.services.transaction.Transaccion") as MockTx, \
             patch("src.services.gamification.update_streak") as mock_streak, \
             patch("src.services.gamification.award_xp") as mock_award:

            db_tx = MagicMock()
            db_tx.id = uuid4()
            MockTx.return_value = db_tx

            svc.create_transaccion(mock_db, schema)

            mock_streak.assert_called_once_with(mock_db, user_id="user_123")
            mock_award.assert_called_once_with(
                mock_db,
                user_id="user_123",
                amount=10,
                event_type="expense_created",
                reference_id=str(db_tx.id)
            )

    def test_no_dispara_gamificacion_si_cuenta_no_existe(self, mock_db):
        schema = self._make_schema()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch("src.services.transaction.Transaccion") as MockTx, \
             patch("src.services.gamification.update_streak") as mock_streak, \
             patch("src.services.gamification.award_xp") as mock_award:

            MockTx.return_value = MagicMock()

            svc.create_transaccion(mock_db, schema)

            mock_streak.assert_not_called()
            mock_award.assert_not_called()

    def test_no_falla_si_gamificacion_lanza_excepcion(self, mock_db):
        schema = self._make_schema()
        cuenta = MagicMock()
        cuenta.usuario_id = "user_123"
        mock_db.query.return_value.filter.return_value.first.return_value = cuenta

        with patch("src.services.transaction.Transaccion") as MockTx, \
             patch("src.services.gamification.update_streak", side_effect=Exception("fallo")):

            MockTx.return_value = MagicMock()

            # No debe propagar la excepción
            resultado = svc.create_transaccion(mock_db, schema)
            assert resultado is not None


class TestGetTransaccionesByCuenta:
    def test_retorna_transacciones_de_la_cuenta(self, mock_db):
        txs = [MagicMock(), MagicMock()]
        mock_db.query.return_value.filter.return_value.all.return_value = txs

        resultado = svc.get_transacciones_by_cuenta(mock_db, uuid4())

        assert resultado == txs

    def test_retorna_lista_vacia_si_no_hay_transacciones(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []

        resultado = svc.get_transacciones_by_cuenta(mock_db, uuid4())

        assert resultado == []
