import asyncio
import websockets
import json
import jwt
import os
from uuid import uuid4

# 1. Configuración: Usa la misma clave secreta que tienes en tu archivo .env
# Si no la tienes a mano, puedes forzarla temporalmente o importarla de tus settings
from src.core.config import settings
SECRET_KEY = settings.jwt_secret_key

# 2. Generamos un token simulado simulando el formato de Clerk
# Usamos un UUID válido porque tu backend (chat.py) lo intenta convertir a UUID para buscar el dashboard
MOCK_TENANT_ID = str(uuid4()) 
mock_payload = {
    "sub": MOCK_TENANT_ID,
    "role": "admin"
}

test_token = jwt.encode(mock_payload, SECRET_KEY, algorithm="HS256")

async def run_chat_client():
    uri = "ws://127.0.0.1:8000/ws/asesor"
    
    print(f"🔄 Conectando a {uri}...")
    async with websockets.connect(uri) as websocket:
        print("✅ Conectado. Enviando token de autenticación...")
        
        # 3. Enviamos el mensaje inicial con el token
        auth_message = {"token": test_token}
        await websocket.send(json.dumps(auth_message))
        
        # Esperamos la respuesta de autenticación
        auth_response = await websocket.recv()
        print(f"📩 Respuesta Auth: {auth_response}")
        
        # 4. Si fue exitoso, mandamos un mensaje de prueba
        print("💬 Enviando pregunta de prueba al IA...")
        chat_message = {"content": "¿Qué es el ISR?"}
        await websocket.send(json.dumps(chat_message))
        
        # 5. Escuchamos las respuestas (status de routing y respuesta final)
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"🤖 IA responde: {response}")
            except asyncio.TimeoutError:
                print("⏳ Fin de la recepción de mensajes (Timeout).")
                break

if __name__ == "__main__":
    asyncio.run(run_chat_client())