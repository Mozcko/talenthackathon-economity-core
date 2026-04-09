"""
Pruebas unitarias para src/services/gamification.py
Todas las pruebas usan mocks — no se requiere base de datos real.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch, call

import src.services.gamification as svc
from src.models.gamification import (
    PerfilGamificacion,
    EventoGamificacion,
    DefinicionLogro,
    LogroUsuario,
)


# ---------------------------------------------------------------------------
# get_profile
# ---------------------------------------------------------------------------

class TestGetProfile:
    def test_retorna_perfil_existente(self, mock_db, perfil_base):
        mock_db.query.return_value.filter.return_value.first.return_value = perfil_base

        resultado = svc.get_profile(mock_db, "user_test_123")

        assert resultado is perfil_base
        mock_db.add.assert_not_called()

    def test_crea_perfil_si_no_existe(self, mock_db):
        # First .first() → no profile; second .first() → user exists
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, MagicMock()]

        with patch("src.services.gamification.PerfilGamificacion") as MockPerfil:
            nuevo_perfil = MagicMock()
            MockPerfil.return_value = nuevo_perfil

            resultado = svc.get_profile(mock_db, "user_nuevo")

            MockPerfil.assert_called_once_with(usuario_id="user_nuevo")
            mock_db.add.assert_called_once_with(nuevo_perfil)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(nuevo_perfil)
            assert resultado is nuevo_perfil


# ---------------------------------------------------------------------------
# award_xp
# ---------------------------------------------------------------------------

class TestAwardXp:
    def test_idempotencia_no_otorga_xp_si_evento_ya_existe(self, mock_db, perfil_base):
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()  # evento existente

        resultado = svc.award_xp(mock_db, "user_test_123", 10, "expense_created", reference_id="ref_123")

        assert resultado is None
        mock_db.add.assert_not_called()

    def test_otorga_xp_sin_reference_id(self, mock_db, perfil_base):
        with patch("src.services.gamification.get_profile", return_value=perfil_base), \
             patch("src.services.gamification.check_achievements"):

            perfil_base.total_xp = 0
            svc.award_xp(mock_db, "user_test_123", 50, "expense_created")

            assert perfil_base.total_xp == 50
            assert perfil_base.nivel_actual == "bronze"
            mock_db.commit.assert_called_once()

    def test_sube_a_silver_al_llegar_a_100_xp(self, mock_db, perfil_base):
        with patch("src.services.gamification.get_profile", return_value=perfil_base), \
             patch("src.services.gamification.check_achievements"):

            perfil_base.total_xp = 90
            svc.award_xp(mock_db, "user_test_123", 10, "expense_created")

            assert perfil_base.total_xp == 100
            assert perfil_base.nivel_actual == "silver"

    def test_sube_a_gold_al_llegar_a_300_xp(self, mock_db, perfil_base):
        with patch("src.services.gamification.get_profile", return_value=perfil_base), \
             patch("src.services.gamification.check_achievements"):

            perfil_base.total_xp = 280
            svc.award_xp(mock_db, "user_test_123", 20, "expense_created")

            assert perfil_base.total_xp == 300
            assert perfil_base.nivel_actual == "gold"

    def test_llama_check_achievements_despues_de_otorgar_xp(self, mock_db, perfil_base):
        with patch("src.services.gamification.get_profile", return_value=perfil_base), \
             patch("src.services.gamification.check_achievements") as mock_check:

            svc.award_xp(mock_db, "user_test_123", 10, "expense_created")

            mock_check.assert_called_once_with(mock_db, "user_test_123")


# ---------------------------------------------------------------------------
# update_streak
# ---------------------------------------------------------------------------

class TestUpdateStreak:
    def test_no_modifica_si_ya_se_registro_hoy(self, mock_db, perfil_base):
        perfil_base.fecha_ultima_actividad = date.today()
        perfil_base.racha_actual = 5

        with patch("src.services.gamification.get_profile", return_value=perfil_base):
            resultado = svc.update_streak(mock_db, "user_test_123")

        assert resultado.racha_actual == 5
        mock_db.commit.assert_not_called()

    def test_incrementa_racha_si_actividad_fue_ayer(self, mock_db, perfil_base):
        perfil_base.fecha_ultima_actividad = date.today() - timedelta(days=1)
        perfil_base.racha_actual = 3
        perfil_base.racha_maxima = 3

        with patch("src.services.gamification.get_profile", return_value=perfil_base), \
             patch("src.services.gamification.award_xp"), \
             patch("src.services.gamification.check_achievements"):

            svc.update_streak(mock_db, "user_test_123")

        assert perfil_base.racha_actual == 4
        assert perfil_base.racha_maxima == 4
        assert perfil_base.fecha_ultima_actividad == date.today()

    def test_reinicia_racha_si_hay_gap_mayor_a_un_dia(self, mock_db, perfil_base):
        perfil_base.fecha_ultima_actividad = date.today() - timedelta(days=3)
        perfil_base.racha_actual = 10
        perfil_base.racha_maxima = 10

        with patch("src.services.gamification.get_profile", return_value=perfil_base), \
             patch("src.services.gamification.award_xp"), \
             patch("src.services.gamification.check_achievements"):

            svc.update_streak(mock_db, "user_test_123")

        assert perfil_base.racha_actual == 1
        assert perfil_base.racha_maxima == 10  # máximo no baja

    def test_otorga_xp_por_checkin_diario(self, mock_db, perfil_base):
        hoy = date.today()
        perfil_base.fecha_ultima_actividad = hoy - timedelta(days=1)
        perfil_base.racha_actual = 1
        perfil_base.racha_maxima = 1

        with patch("src.services.gamification.get_profile", return_value=perfil_base), \
             patch("src.services.gamification.award_xp") as mock_award, \
             patch("src.services.gamification.check_achievements"):

            svc.update_streak(mock_db, "user_test_123")

            mock_award.assert_called_once_with(
                mock_db, "user_test_123",
                amount=5,
                event_type="daily_checkin",
                reference_id=str(hoy)
            )


# ---------------------------------------------------------------------------
# unlock_achievement
# ---------------------------------------------------------------------------

class TestUnlockAchievement:
    def test_no_hace_nada_si_definicion_no_existe(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        svc.unlock_achievement(mock_db, "user_test_123", "logro_inexistente")

        mock_db.add.assert_not_called()

    def test_crea_logro_y_otorga_xp_recompensa(self, mock_db):
        definicion = MagicMock(spec=DefinicionLogro)
        definicion.xp_recompensa = 50
        mock_db.query.return_value.filter.return_value.first.return_value = definicion

        with patch("src.services.gamification.LogroUsuario") as MockLogro, \
             patch("src.services.gamification.award_xp") as mock_award:

            nuevo_logro = MagicMock()
            MockLogro.return_value = nuevo_logro

            svc.unlock_achievement(mock_db, "user_test_123", "first_expense")

            MockLogro.assert_called_once_with(usuario_id="user_test_123", codigo_logro="first_expense")
            mock_db.add.assert_called_once_with(nuevo_logro)
            mock_db.commit.assert_called_once()
            mock_award.assert_called_once_with(
                mock_db, "user_test_123",
                amount=50,
                event_type="achievement_unlock",
                reference_id="first_expense"
            )


# ---------------------------------------------------------------------------
# check_achievements
# ---------------------------------------------------------------------------

class TestCheckAchievements:
    def test_no_desbloquea_logro_ya_desbloqueado(self, mock_db, perfil_base):
        logro_existente = MagicMock()
        logro_existente.codigo_logro = "streak_3"
        perfil_base.racha_maxima = 5
        perfil_base.total_xp = 0

        mock_db.query.return_value.filter.return_value.all.return_value = [logro_existente]
        mock_db.query.return_value.filter.return_value.scalar.return_value = 0  # 0 eventos de gasto

        with patch("src.services.gamification.get_profile", return_value=perfil_base), \
             patch("src.services.gamification.unlock_achievement") as mock_unlock:

            svc.check_achievements(mock_db, "user_test_123")

            # streak_3 ya estaba desbloqueado, no debe volver a desbloquearse
            desbloqueados = [c[0][2] for c in mock_unlock.call_args_list]
            assert "streak_3" not in desbloqueados

    def test_desbloquea_streak_3_cuando_racha_maxima_es_3(self, mock_db, perfil_base):
        perfil_base.racha_maxima = 3
        perfil_base.total_xp = 0

        mock_db.query.return_value.filter.return_value.all.return_value = []  # sin logros previos
        # Para el conteo de eventos (first_expense)
        mock_db.query.return_value.filter.return_value.scalar.return_value = 0

        with patch("src.services.gamification.get_profile", return_value=perfil_base), \
             patch("src.services.gamification.unlock_achievement") as mock_unlock:

            svc.check_achievements(mock_db, "user_test_123")

            codigos = [c[0][2] for c in mock_unlock.call_args_list]
            assert "streak_3" in codigos


# ---------------------------------------------------------------------------
# get_next_milestone
# ---------------------------------------------------------------------------

class TestGetNextMilestone:
    def test_retorna_hito_silver_si_xp_menor_a_100(self, mock_db, perfil_base):
        perfil_base.total_xp = 40

        with patch("src.services.gamification.get_profile", return_value=perfil_base):
            resultado = svc.get_next_milestone(mock_db, "user_test_123")

        assert resultado["xp_objetivo"] == 100
        assert resultado["completado"] is False
        assert "Plata" in resultado["mensaje"]
        assert 0 < resultado["progreso"] <= 100

    def test_retorna_hito_gold_si_xp_entre_100_y_300(self, mock_db, perfil_base):
        perfil_base.total_xp = 150

        with patch("src.services.gamification.get_profile", return_value=perfil_base):
            resultado = svc.get_next_milestone(mock_db, "user_test_123")

        assert resultado["xp_objetivo"] == 300
        assert resultado["completado"] is False
        assert "Oro" in resultado["mensaje"]

    def test_retorna_completado_si_xp_mayor_o_igual_a_300(self, mock_db, perfil_base):
        perfil_base.total_xp = 350

        with patch("src.services.gamification.get_profile", return_value=perfil_base):
            resultado = svc.get_next_milestone(mock_db, "user_test_123")

        assert resultado["completado"] is True
        assert resultado["progreso"] == 100.0
        assert resultado["xp_objetivo"] is None


# ---------------------------------------------------------------------------
# get_calculated_profile
# ---------------------------------------------------------------------------

class TestGetCalculatedProfile:
    def test_retorna_campos_correctos_en_bronze(self, mock_db, perfil_base):
        perfil_base.total_xp = 50
        perfil_base.nivel_actual = "bronze"
        perfil_base.racha_actual = 2
        perfil_base.racha_maxima = 5
        perfil_base.fecha_ultima_actividad = date.today()

        with patch("src.services.gamification.get_profile", return_value=perfil_base):
            resultado = svc.get_calculated_profile(mock_db, "user_test_123")

        assert resultado["usuario_id"] == "user_test_123"
        assert resultado["total_xp"] == 50
        assert resultado["nivel_actual"] == "bronze"
        assert resultado["siguiente_nivel"] == "silver"
        assert resultado["xp_para_siguiente_nivel"] == 50
        assert 0 < resultado["porcentaje_progreso"] <= 100

    def test_progreso_es_100_en_nivel_maximo(self, mock_db, perfil_base):
        perfil_base.total_xp = 2000
        perfil_base.nivel_actual = "mythic"
        perfil_base.racha_actual = 0
        perfil_base.racha_maxima = 0
        perfil_base.fecha_ultima_actividad = None

        with patch("src.services.gamification.get_profile", return_value=perfil_base):
            resultado = svc.get_calculated_profile(mock_db, "user_test_123")

        assert resultado["siguiente_nivel"] is None
        assert resultado["xp_para_siguiente_nivel"] is None
        assert resultado["porcentaje_progreso"] == 100.0
