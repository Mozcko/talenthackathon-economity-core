import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from io import BytesIO

from src.main import app
from src.core.security import get_current_user_token

# 1. Simulamos un usuario autenticado
def override_get_current_user_token():
    return {"sub": "test_user_123", "role": "admin"}

# Reemplazamos la validación real por nuestra simulación
app.dependency_overrides[get_current_user_token] = override_get_current_user_token

client = TestClient(app)

# 2. Datos simulados que retornaría GPT-4o
MOCK_EXTRACTION_DATA = {
    "monto": 150.0,
    "descripcion": "Café de Starbucks",
    "es_ingreso": False,
    "categoria_sugerida": "Alimentos",
    "texto_original": "Pagué 150 por un café"
}

@patch("src.api.routers.upload.extraction_agent.extraer_datos_texto_async", new_callable=AsyncMock)
def test_procesar_texto(mock_extraer):
    # Configuramos el mock para que devuelva nuestro diccionario de prueba
    mock_extraer.return_value = MOCK_EXTRACTION_DATA
    
    response = client.post("/upload/texto", json={"texto": "Pagué 150 por un café"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["monto"] == 150.0
    assert data["descripcion"] == "Café de Starbucks"
    mock_extraer.assert_called_once_with("Pagué 150 por un café")

@patch("src.api.routers.upload.extraction_agent.extraer_datos_audio_async", new_callable=AsyncMock)
def test_procesar_audio(mock_extraer):
    mock_extraer.return_value = MOCK_EXTRACTION_DATA
    
    # Simulamos un archivo de audio en memoria (BytesIO)
    audio_file = BytesIO(b"contenido binario de audio falso")
    
    response = client.post(
        "/upload/audio", 
        files={"file": ("test.m4a", audio_file, "audio/mp4")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["categoria_sugerida"] == "Alimentos"
    # Verificamos que nuestro agente fue llamado
    mock_extraer.assert_called_once()

@patch("src.api.routers.upload.extraction_agent.extraer_datos_imagen_async", new_callable=AsyncMock)
def test_procesar_imagen(mock_extraer):
    mock_extraer.return_value = MOCK_EXTRACTION_DATA
    
    # Simulamos un archivo de imagen en memoria
    image_file = BytesIO(b"contenido binario de imagen falso")
    
    response = client.post(
        "/upload/imagen", 
        files={"file": ("ticket.jpg", image_file, "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["es_ingreso"] is False
    mock_extraer.assert_called_once()