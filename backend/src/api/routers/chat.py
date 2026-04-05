# src/api/routers/chat.py
import json
import jwt
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.config import settings
from src.services.dashboard import get_dashboard_summary

# Importaciones de los Agentes IA
from src.services.ai.router import clasificar_intencion_async
from src.services.ai.memory import formatear_historial
from src.services.ai.agents.fiscal_agent import consultar_rag_fiscal_async
from src.services.ai.agents.math_agent import calcular_proyeccion_async
from src.services.ai.agents.data_agent import analizar_datos_async

# Importaciones de LangChain para el chat general
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

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

def validar_token_ws(token: str) -> str:
    """Valida el JWT en el entorno WebSocket y retorna el tenant_id."""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=["HS256", "RS256"], 
            options={"verify_aud": False}
        )
        return payload.get("sub")
    except Exception:
        return None

@router.websocket("/asesor")
async def chat_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    tenant_id_str = None
    contexto_financiero = ""
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                
                # 1. Autenticación en el primer mensaje
                if not tenant_id_str and "token" in payload:
                    tenant_id_str = validar_token_ws(payload["token"])
                    if not tenant_id_str:
                        await manager.send_message("❌ Token inválido o expirado. Desconectando...", websocket)
                        await websocket.close()
                        return
                    
                    # Generamos el contexto financiero en tiempo real
                    tenant_uuid = UUID(tenant_id_str) if isinstance(tenant_id_str, str) and '-' in tenant_id_str else tenant_id_str
                    resumen = get_dashboard_summary(db, tenant_uuid, tenant_id_str)
                    
                    contexto_financiero = (
                        f"Contexto del usuario actual:\n"
                        f"- Saldo Total: ${resumen['saldo_total']}\n"
                        f"- Flujo de Caja Libre: ${resumen['flujo_caja_mensual']}\n"
                        f"- Score de Resiliencia: {resumen['score_resiliencia']}\n"
                    )
                    if resumen.get('meta_proxima'):
                        contexto_financiero += f"- Meta próxima: {resumen['meta_proxima'].nombre} (Objetivo: ${resumen['meta_proxima'].monto_objetivo})\n"
                    
                    await manager.send_status("autenticado", websocket)
                    continue # Esperamos el siguiente mensaje que ya contendrá la pregunta del usuario

                contenido = payload.get("content", "")
                historial_raw = payload.get("history", [])
            except json.JSONDecodeError:
                contenido = data
                historial_raw = []
            
            # Si intenta hablar antes de mandar el token
            if not tenant_id_str:
                await manager.send_message("⚠️ Por favor, envía tu token de autenticación primero.", websocket)
                continue

            historial_texto = formatear_historial(historial_raw)
            
            # Inyectamos la realidad del usuario al historial para que todos los agentes la lean
            historial_enriquecido = f"{contexto_financiero}\n\nHistorial de charla:\n{historial_texto}"

            # 2. Enrutamiento Semántico
            await manager.send_status("analizando intención...", websocket)
            categoria = await clasificar_intencion_async(contenido)
            
            # 3. Ejecución Delegada a los Agentes Especializados
            if categoria == "CONSULTA_FISCAL":
                await manager.send_status("consultando leyes y contexto...", websocket)
                respuesta = await consultar_rag_fiscal_async(contenido, historial_enriquecido)
                
            elif categoria == "PROYECCION_MATEMATICA":
                await manager.send_status("calculando proyección financiera...", websocket)
                respuesta = await calcular_proyeccion_async(contenido, historial_enriquecido)
                
            elif categoria == "ANALISIS_DATOS":
                await manager.send_status("analizando tu historial de gastos...", websocket)
                respuesta = await analizar_datos_async(contenido, historial_enriquecido, tenant_id_str)
                
            else:
                await manager.send_status("escribiendo...", websocket)
                # Respuesta general del Arquitecto Financiero Base
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=settings.openai_api_key)
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "Eres Economity, un arquitecto financiero amigable. Responde de manera concisa. Aquí están los datos del usuario para que le des consejos personalizados: {contexto}"),
                    ("human", "{pregunta}")
                ])
                chain = prompt | llm
                res = await chain.ainvoke({"contexto": contexto_financiero, "pregunta": contenido})
                respuesta = res.content

            # 4. Enviar respuesta final
            await manager.send_message(respuesta, websocket)
            await manager.send_status("idle", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_message(f"❌ Error en el motor cognitivo: {str(e)}", websocket)
        manager.disconnect(websocket)