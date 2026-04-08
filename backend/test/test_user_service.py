"""
Pruebas unitarias para src/services/user.py
"""
import pytest
from unittest.mock import MagicMock, patch

import src.services.user as svc
from src.models.user import Usuario, CuentaFinanciera


class TestCreateUsuario:
    def test_persiste_usuario_y_lo_retorna(self, mock_db):
        schema = MagicMock()
        schema.model_dump.return_value = {"id": "user_1", "tenant_id": "t1"}

        with patch("src.services.user.Usuario") as MockUsuario:
            db_user = MagicMock()
            MockUsuario.return_value = db_user

            resultado = svc.create_usuario(mock_db, schema)

            MockUsuario.assert_called_once_with(id="user_1", tenant_id="t1")
            mock_db.add.assert_called_once_with(db_user)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(db_user)
            assert resultado is db_user


class TestGetUsuario:
    def test_retorna_usuario_existente(self, mock_db):
        usuario = MagicMock(spec=Usuario)
        mock_db.query.return_value.filter.return_value.first.return_value = usuario

        resultado = svc.get_usuario(mock_db, "user_1")

        assert resultado is usuario

    def test_retorna_none_si_no_existe(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        resultado = svc.get_usuario(mock_db, "inexistente")

        assert resultado is None


class TestGetUsuarios:
    def test_retorna_lista_paginada(self, mock_db):
        usuarios = [MagicMock(), MagicMock()]
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = usuarios

        resultado = svc.get_usuarios(mock_db, skip=0, limit=10)

        assert resultado == usuarios
        mock_db.query.return_value.offset.assert_called_once_with(0)
        mock_db.query.return_value.offset.return_value.limit.assert_called_once_with(10)

    def test_usa_valores_por_defecto(self, mock_db):
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = []

        svc.get_usuarios(mock_db)

        mock_db.query.return_value.offset.assert_called_once_with(0)
        mock_db.query.return_value.offset.return_value.limit.assert_called_once_with(100)


class TestCreateCuentaFinanciera:
    def test_persiste_cuenta_y_la_retorna(self, mock_db):
        schema = MagicMock()
        schema.model_dump.return_value = {"nombre": "Nómina", "tipo": "Debito"}

        with patch("src.services.user.CuentaFinanciera") as MockCuenta:
            db_cuenta = MagicMock()
            MockCuenta.return_value = db_cuenta

            resultado = svc.create_cuenta_financiera(mock_db, schema)

            MockCuenta.assert_called_once_with(nombre="Nómina", tipo="Debito")
            mock_db.add.assert_called_once_with(db_cuenta)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(db_cuenta)
            assert resultado is db_cuenta


class TestGetCuentasByUsuario:
    def test_retorna_cuentas_del_usuario(self, mock_db):
        cuentas = [MagicMock(), MagicMock()]
        mock_db.query.return_value.filter.return_value.all.return_value = cuentas

        resultado = svc.get_cuentas_by_usuario(mock_db, "user_1")

        assert resultado == cuentas

    def test_retorna_lista_vacia_si_no_hay_cuentas(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []

        resultado = svc.get_cuentas_by_usuario(mock_db, "user_sin_cuentas")

        assert resultado == []
