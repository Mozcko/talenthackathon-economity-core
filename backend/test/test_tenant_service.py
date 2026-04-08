"""
Pruebas unitarias para src/services/tenant.py
"""
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

import src.services.tenant as svc
from src.models.tenant import Tenant


class TestCreateTenant:
    def test_persiste_tenant_y_lo_retorna(self, mock_db):
        schema = MagicMock()
        schema.model_dump.return_value = {"nombre": "Empresa ABC"}

        with patch("src.services.tenant.Tenant") as MockTenant:
            db_tenant = MagicMock()
            MockTenant.return_value = db_tenant

            resultado = svc.create_tenant(mock_db, schema)

            MockTenant.assert_called_once_with(nombre="Empresa ABC")
            mock_db.add.assert_called_once_with(db_tenant)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(db_tenant)
            assert resultado is db_tenant


class TestGetTenant:
    def test_retorna_tenant_existente(self, mock_db):
        tenant = MagicMock(spec=Tenant)
        mock_db.query.return_value.filter.return_value.first.return_value = tenant

        resultado = svc.get_tenant(mock_db, uuid4())

        assert resultado is tenant

    def test_retorna_none_si_no_existe(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        resultado = svc.get_tenant(mock_db, uuid4())

        assert resultado is None
