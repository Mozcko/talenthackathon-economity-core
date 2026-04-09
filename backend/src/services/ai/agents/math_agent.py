# src/services/ai/agents/math_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from src.core.config import settings
 
@tool
def calcular_interes_compuesto(capital_inicial: float, aportacion_mensual: float, tasa_anual: float, anos: int) -> dict:
    """
    Calcula la proyección de inversión usando la fórmula de interés compuesto.
    """
    tasa_mensual = tasa_anual / 12 / 100
    meses = anos * 12
    saldo = capital_inicial
    
    for _ in range(meses):
        saldo += aportacion_mensual
        saldo *= (1 + tasa_mensual)
        
    rendimiento_total = saldo - (capital_inicial + (aportacion_mensual * meses))
    
    return {
        "saldo_final": round(float(saldo), 2),
        "total_aportado": round(float(capital_inicial + (aportacion_mensual * meses)), 2),
        "rendimiento_ganado": round(float(rendimiento_total), 2)
    }

async def calcular_proyeccion_async(pregunta: str, historial: str) -> str:
    """Agente que evalúa la pregunta e invoca la herramienta matemática."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=settings.openai_api_key)
    tools = [calcular_interes_compuesto]
    llm_with_tools = llm.bind_tools(tools)
    
    mensajes = [
        SystemMessage(content=f"Eres el Agente Matemático de Economity. Usa SIEMPRE la herramienta 'calcular_interes_compuesto'.\nHistorial:\n{historial}"),
        HumanMessage(content=pregunta)
    ]
    
    # 1. El LLM decide si llama a la herramienta
    respuesta_ai = await llm_with_tools.ainvoke(mensajes)
    mensajes.append(respuesta_ai)
    
    # 2. Si el LLM decide usar la herramienta, la ejecutamos
    if hasattr(respuesta_ai, "tool_calls") and respuesta_ai.tool_calls:
        for tool_call in respuesta_ai.tool_calls:
            if tool_call["name"] == "calcular_interes_compuesto":
                resultado = calcular_interes_compuesto.invoke(tool_call["args"])
                mensajes.append(ToolMessage(tool_call_id=tool_call["id"], content=str(resultado)))
        
        # 3. El LLM formula su respuesta final basada en el resultado de la función
        respuesta_final = await llm_with_tools.ainvoke(mensajes)
        return str(respuesta_final.content)
        
    # Si el LLM no usó la herramienta, retornamos su respuesta inicial
    return str(respuesta_ai.content)