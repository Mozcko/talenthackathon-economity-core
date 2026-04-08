"""
Pruebas unitarias para src/services/goal.py
"""
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from decimal import Decimal

import src.services.goal as svc


class TestCreateMeta:
    def test_persiste_meta_y_la_retorna(self, mock_db):
        schema = MagicMock()
        schema.model_dump.return_value = {"nombre": "Fondo de emergencia", "monto_objetivo": Decimal("10000")}

        with patch("src.services.goal.MetaFinanciera") as MockMeta:
            db_meta = MagicMock()
            MockMeta.return_value = db_meta

            resultado = svc.create_meta(mock_db, schema)

            MockMeta.assert_called_once_with(nombre="Fondo de emergencia", monto_objetivo=Decimal("10000"))
            mock_db.add.assert_called_once_with(db_meta)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(db_meta)
            assert resultado is db_meta


class TestGetMetasByUsuario:
    def test_retorna_metas_del_tenant(self, mock_db):
        metas = [MagicMock(), MagicMock()]
        mock_db.query.return_value.filter.return_value.all.return_value = metas

        resultado = svc.get_metas_by_usuario(mock_db, uuid4())

        assert resultado == metas

    def test_retorna_lista_vacia_si_no_hay_metas(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []

        resultado = svc.get_metas_by_usuario(mock_db, uuid4())

        assert resultado == []


class TestAddProgresoMeta:
    def test_suma_monto_al_progreso_y_retorna_meta(self, mock_db):
        db_meta = MagicMock()
        db_meta.progreso_actual = Decimal("200")
        # filter() recibe múltiples argumentos en una sola llamada
        mock_db.query.return_value.filter.return_value.first.return_value = db_meta

        resultado = svc.add_progreso_meta(mock_db, uuid4(), Decimal("300"), uuid4())

        assert db_meta.progreso_actual == Decimal("500")
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(db_meta)
        assert resultado is db_meta

    def test_retorna_none_si_meta_no_existe(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        resultado = svc.add_progreso_meta(mock_db, uuid4(), Decimal("100"), uuid4())

        assert resultado is None
        mock_db.commit.assert_not_called()


class TestDeleteMeta:
    def test_elimina_meta_y_retorna_true(self, mock_db):
        db_meta = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = db_meta

        resultado = svc.delete_meta(mock_db, uuid4(), uuid4())

        mock_db.delete.assert_called_once_with(db_meta)
        mock_db.commit.assert_called_once()
        assert resultado is True

    def test_retorna_false_si_meta_no_existe(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        resultado = svc.delete_meta(mock_db, uuid4(), uuid4())

        mock_db.delete.assert_not_called()
        assert resultado is False
