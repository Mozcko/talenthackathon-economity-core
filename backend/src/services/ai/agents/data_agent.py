# src/services/ai/agents/data_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from src.core.config import settings
from src.core.database import SessionLocal
from src.models.transaction import Transaccion, SubCategoria

@tool
def obtener_resumen_transacciones(tenant_id: str) -> str:
    """
    Obtiene todo el historial de transacciones, ingresos y gastos del usuario.
    Requiere el tenant_id (ID del usuario) para buscar en la base de datos.
    """
    db = SessionLocal()
    try:
        # Hacemos un JOIN para traer el nombre de la categoría junto con el gasto
        resultados = db.query(Transaccion, SubCategoria).join(
            SubCategoria, Transaccion.sub_categoria_id == SubCategoria.id
        ).filter(
            # Forzamos a string para evitar conflictos de tipo UUID en la query
            cast(Transaccion.tenant_id, String) == tenant_id 
        ).order_by(Transaccion.fecha_operacion.desc()).all()
        
        if not resultados:
            return "No hay transacciones registradas."
            
        resumen = []
        for t, s in resultados:
            fecha = t.fecha_operacion.strftime('%Y-%m-%d')
            tipo = "Ingreso" if s.categoria_id == 1 else "Gasto"
            resumen.append(f"[{fecha}] {tipo} - Categoría: {s.nombre} | Monto: ${t.monto} | Desc: {t.descripcion or 'N/A'}")
            
        return "\n".join(resumen)
    except Exception as e:
        return f"Error al consultar base de datos: {str(e)}"
    finally:
        db.close()

# Necesitamos importar cast y String para la query de arriba
from sqlalchemy import cast, String

async def analizar_datos_async(pregunta: str, historial: str, tenant_id: str) -> str:
    """Agente que analiza el historial de gastos del usuario."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=settings.openai_api_key)
    tools = [obtener_resumen_transacciones]
    llm_with_tools = llm.bind_tools(tools)
    
    # Le inyectamos el tenant_id en el System Prompt para que sepa quién es el usuario
    # y lo use OBLIGATORIAMENTE al llamar a la herramienta.
    mensajes = [
        SystemMessage(content=f"Eres el Analista de Datos de Economity. El ID del usuario actual es '{tenant_id}'. "
                              f"Usa la herramienta 'obtener_resumen_transacciones' pasando ese ID exacto para leer sus gastos. "
                              f"Analiza sus datos, suma si es necesario, y dale insights financieros claros.\n"
                              f"Historial:\n{historial}"),
        HumanMessage(content=pregunta)
    ]
    
    respuesta_ai = await llm_with_tools.ainvoke(mensajes)
    mensajes.append(respuesta_ai)
    
    if hasattr(respuesta_ai, "tool_calls") and respuesta_ai.tool_calls:
        for tool_call in respuesta_ai.tool_calls:
            if tool_call["name"] == "obtener_resumen_transacciones":
                resultado = obtener_resumen_transacciones.invoke(tool_call["args"])
                mensajes.append(ToolMessage(tool_call_id=tool_call["id"], content=str(resultado)))
                
        respuesta_final = await llm_with_tools.ainvoke(mensajes)
        return str(respuesta_final.content)
        
    return str(respuesta_ai.content)