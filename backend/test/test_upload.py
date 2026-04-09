import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from io import BytesIO

from src.main import app
from src.core.security import get_current_user_token
from src.core.database import get_db

# 1. Simulamos un usuario autenticado
def override_get_current_user_token():
    return {"sub": "test_user_123", "role": "admin"}

# 2. Simulamos la base de datos
def override_get_db():
    yield MagicMock()

app.dependency_overrides[get_current_user_token] = override_get_current_user_token
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 2. Datos simulados que retornaría GPT-4o
MOCK_EXTRACTION_DATA = {
    "monto": 150.0,
    "descripcion": "Café de Starbucks",
    "es_ingreso": False,
    "categoria_sugerida": "Alimentos",
    "texto_original": "Pagué 150 por un café"
}

@patch("src.api.routers.upload.resolve_sub_categoria_id", return_value=3)
@patch("src.api.routers.upload.extraction_agent.extraer_datos_texto_async", new_callable=AsyncMock)
def test_procesar_texto(mock_extraer, mock_resolve):
    mock_extraer.return_value = dict(MOCK_EXTRACTION_DATA)

    response = client.post("/upload/texto", json={"texto": "Pagué 150 por un café"})

    assert response.status_code == 200
    data = response.json()
    assert data["monto"] == 150.0
    assert data["descripcion"] == "Café de Starbucks"
    assert data["sub_categoria_id"] == 3
    mock_extraer.assert_called_once_with("Pagué 150 por un café")

@patch("src.api.routers.upload.resolve_sub_categoria_id", return_value=3)
@patch("src.api.routers.upload.extraction_agent.extraer_datos_audio_async", new_callable=AsyncMock)
def test_procesar_audio(mock_extraer, mock_resolve):
    mock_extraer.return_value = dict(MOCK_EXTRACTION_DATA)

    audio_file = BytesIO(b"contenido binario de audio falso")
    response = client.post(
        "/upload/audio",
        files={"file": ("test.m4a", audio_file, "audio/mp4")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["categoria_sugerida"] == "Alimentos"
    assert data["sub_categoria_id"] == 3
    mock_extraer.assert_called_once()

@patch("src.api.routers.upload.resolve_sub_categoria_id", return_value=3)
@patch("src.api.routers.upload.extraction_agent.extraer_datos_imagen_async", new_callable=AsyncMock)
def test_procesar_imagen(mock_extraer, mock_resolve):
    mock_extraer.return_value = dict(MOCK_EXTRACTION_DATA)

    image_file = BytesIO(b"contenido binario de imagen falso")
    response = client.post(
        "/upload/imagen",
        files={"file": ("ticket.jpg", image_file, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["es_ingreso"] is False
    assert data["sub_categoria_id"] == 3
    mock_extraer.assert_called_once()