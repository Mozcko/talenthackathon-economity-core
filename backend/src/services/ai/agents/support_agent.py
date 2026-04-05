# src/services/ai/agents/support_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.core.config import settings

async def soporte_general_async(pregunta: str, historial: str) -> str:
    """Agente dedicado a resolver dudas de la app, saludar y dar educación básica."""
    # Usamos temperatura 0.5 para que sea un poco más conversacional y empático
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, api_key=settings.openai_api_key)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres el Agente de Soporte de Economity, un asistente financiero empático y profesional. "
                   "Tu rol es saludar, explicar cómo usar la aplicación y dar educación financiera básica. "
                   "Si te piden consejos de inversión, recuérdales que no eres un asesor financiero certificado, "
                   "pero puedes sugerirles revisar la Tier List de la app.\n"
                   "Contexto e Historial:\n{historial}"),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    respuesta = await chain.ainvoke({"input": pregunta, "historial": historial})
    return respuesta.content