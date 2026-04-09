# src/api/routers/chat.py
import json
import jwt
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.config import settings
from src.core.security import _get_jwks_client
from src.models.user import Usuario
from src.models.tenant import Tenant
from src.services.dashboard import get_dashboard_summary

# Importaciones de los Agentes IA y el Router Semántico
from src.services.ai.router import clasificar_intencion_async
from src.services.ai.memory import formatear_historial
from src.services.ai.agents.fiscal_agent import consultar_rag_fiscal_async
from src.services.ai.agents.math_agent import calcular_proyeccion_async
from src.services.ai.agents.data_agent import analizar_datos_async
from src.services.ai.agents.support_agent import soporte_general_async

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
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")

    try:
        if settings.clerk_jwks_url:
            signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
        elif settings.jwt_secret_key:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        else:
            print("❌ Auth no configurada: define CLERK_JWKS_URL o JWT_SECRET_KEY en .env")
            return None

        return payload.get("sub")
    except Exception as e:
        print(f"❌ Error al decodificar token WS: {str(e)}")
        return None

@router.websocket("/asesor")
async def chat_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    user_id = None
    tenant_uuid = None
    contexto_financiero = ""

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)

                # 1. Autenticación en el primer mensaje
                if not user_id and "token" in payload:
                    user_id = validar_token_ws(payload["token"])
                    if not user_id:
                        await manager.send_message("❌ Token inválido o expirado. Desconectando...", websocket)
                        await websocket.close()
                        return

                    # Obtener o auto-provisionar usuario y tenant en el primer login
                    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
                    if not usuario:
                        nuevo_tenant = Tenant(nombre=f"Personal de {user_id}")
                        db.add(nuevo_tenant)
                        db.flush()  # Genera el UUID sin commit aún
                        usuario = Usuario(id=user_id, tenant_id=nuevo_tenant.id)
                        db.add(usuario)
                        db.commit()
                        db.refresh(usuario)
                    tenant_uuid = usuario.tenant_id

                    await manager.send_status("autenticado", websocket)
                    continue # Esperamos el siguiente mensaje que ya contendrá la pregunta del usuario

                contenido = payload.get("content", "")
                historial_raw = payload.get("history", [])
            except json.JSONDecodeError:
                contenido = data
                historial_raw = []
            
            # Si intenta hablar antes de mandar el token
            if not user_id:
                await manager.send_message("⚠️ Por favor, envía tu token de autenticación primero.", websocket)
                continue

            historial_texto = formatear_historial(historial_raw)

            # Recalculamos el contexto financiero en cada mensaje para que siempre sea actual
            resumen = get_dashboard_summary(db, tenant_uuid, user_id)
            contexto_financiero = (
                f"Contexto financiero actual del usuario:\n"
                f"- Saldo Total (suma de transacciones): ${resumen['saldo_total']}\n"
                f"- Flujo de Caja Libre: ${resumen['flujo_caja_mensual']}\n"
                f"- Score de Resiliencia: {resumen['score_resiliencia']}\n"
            )
            if resumen.get('meta_proxima'):
                contexto_financiero += f"- Meta próxima: {resumen['meta_proxima'].nombre} (Objetivo: ${resumen['meta_proxima'].monto_objetivo})\n"

            # Inyectamos la realidad del usuario al historial para que todos los agentes la lean
            historial_enriquecido = f"{contexto_financiero}\n\nHistorial de charla:\n{historial_texto}"

            # 2. Enrutamiento Semántico y Guardrail
            await manager.send_status("analizando intención y seguridad...", websocket)
            categoria = await clasificar_intencion_async(contenido)
            
            # --- PROTECCIÓN ANTI PROMPT-INJECTION ---
            if categoria == "BLOQUEADO":
                await manager.send_status("escribiendo...", websocket)
                respuesta = "Lo siento, como Arquitecto Financiero de Economity, mi función está estrictamente limitada a temas de finanzas personales, inversiones y uso de la aplicación. No puedo ayudarte con esa solicitud."
                
            # 3. Ejecución Delegada a los Agentes Especializados
            elif categoria == "CONSULTA_FISCAL":
                await manager.send_status("consultando leyes y contexto...", websocket)
                respuesta = await consultar_rag_fiscal_async(contenido, historial_enriquecido)
                
            elif categoria == "PROYECCION_MATEMATICA":
                await manager.send_status("calculando proyección financiera...", websocket)
                respuesta = await calcular_proyeccion_async(contenido, historial_enriquecido)
                
            elif categoria == "ANALISIS_DATOS":
                await manager.send_status("analizando tu historial de gastos...", websocket)
                respuesta = await analizar_datos_async(contenido, historial_enriquecido, str(tenant_uuid))
                
            elif categoria == "SOPORTE_GENERAL":
                await manager.send_status("escribiendo...", websocket)
                respuesta = await soporte_general_async(contenido, historial_enriquecido)
                
            else:
                # Fallback por si el router devuelve algo inesperado
                await manager.send_status("escribiendo...", websocket)
                respuesta = "He recibido tu mensaje, pero no estoy seguro de cómo procesarlo. ¿Podrías reformular tu duda financiera?"

            # 4. Enviar respuesta final
            await manager.send_message(respuesta, websocket)
            await manager.send_status("idle", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_message(f"❌ Error en el motor cognitivo: {str(e)}", websocket)
        manager.disconnect(websocket)