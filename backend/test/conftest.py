import pytest
from unittest.mock import MagicMock
from datetime import date


@pytest.fixture
def mock_db():
    """Sesión de base de datos simulada."""
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db


@pytest.fixture
def perfil_base():
    """Perfil de gamificación base para pruebas."""
    from src.models.gamification import PerfilGamificacion
    perfil = MagicMock(spec=PerfilGamificacion)
    perfil.usuario_id = "user_test_123"
    perfil.total_xp = 0
    perfil.nivel_actual = "bronze"
    perfil.racha_actual = 0
    perfil.racha_maxima = 0
    perfil.fecha_ultima_actividad = None
    return perfil
