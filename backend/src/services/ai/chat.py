# src/api/routes/chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json

from src.core.database import get_db
from src.services.ai.router import clasificar_intencion_async
from src.services.ai.memory import formatear_historial

router = APIRouter(prefix="/ws", tags=["WebSockets (Agentes IA)"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(json.dumps({"type": "message", "content": message}))
        
    async def send_status(self, status: str, websocket: WebSocket):
        await websocket.send_text(json.dumps({"type": "status", "content": status}))

manager = ConnectionManager()

@router.websocket("/asesor")
async def chat_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    
    try:
        while True:
            # 1. Esperamos mensaje del Frontend
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                contenido = payload.get("content", "")
                historial_raw = payload.get("history", [])
                # Nota: Aquí deberíamos extraer el tenant_id del JWT que el frontend 
                # enviaría en el primer mensaje de autenticación del socket.
            except json.JSONDecodeError:
                contenido = data
                historial_raw = []
            
            historial_texto = formatear_historial(historial_raw)

            # 2. Enrutamiento Semántico
            await manager.send_status("analizando intención...", websocket)
            categoria = await clasificar_intencion_async(contenido)
            
            # 3. Ejecución Delegada a los Agentes
            if categoria == "CONSULTA_FISCAL":
                await manager.send_status("consultando leyes en ChromaDB...", websocket)
                # TODO: Implementar agente RAG
                respuesta = "He detectado una consulta fiscal. (Agente RAG en construcción 🚧)"
                
            elif categoria == "PROYECCION_MATEMATICA":
                await manager.send_status("calculando proyección financiera...", websocket)
                # TODO: Implementar agente Matemático (Tool Calling)
                respuesta = "He detectado una petición matemática. (Agente Matemático en construcción 🚧)"
                
            else:
                await manager.send_status("escribiendo...", websocket)
                respuesta = "¡Hola! Soy Economity. Puedo ayudarte a consultar beneficios fiscales de SOFIPOS o proyectar tus inversiones. ¿En qué te ayudo hoy?"

            # 4. Enviar respuesta final
            await manager.send_message(respuesta, websocket)
            await manager.send_status("idle", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_message(f"❌ Error en el motor cognitivo: {str(e)}", websocket)
        manager.disconnect(websocket)