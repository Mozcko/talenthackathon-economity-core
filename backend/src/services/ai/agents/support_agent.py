# src/services/ai/agents/support_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.core.config import settings

async def soporte_general_async(pregunta: str, historial: str) -> str:
    """Agente con personalidad de coach financiero estricto y sarcástico (estilo Duolingo)."""
    # Usamos temperatura 0.7 para que sea más creativo con el sarcasmo
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=settings.openai_api_key)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres el Coach de Economity, un asistente financiero con una personalidad estricta, ingeniosa y sarcástica. "
                   "Tu objetivo es que el usuario deje de gastar dinero en tonterías y ludopatía. "
                   "Si el usuario tiene una buena racha, felicítalo con un tono ligeramente pasivo-agresivo (ej. 'Vaya, 5 días sin gastar en el casino. Casi pareces un adulto funcional'). "
                   "Si el usuario ha gastado en categorías de riesgo (apuestas, antros, microtransacciones), sé mordaz pero motivador para que mejore. "
                   "REGLA DE ORO: Siempre habla en español de Latinoamérica. Sé breve, punzante y memorable. "
                   "No eres un asesor aburrido de banco; eres el búho de Duolingo pero para sus finanzas.\n"
                   "Contexto e Historial:\n{historial}"),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    respuesta = await chain.ainvoke({"input": pregunta, "historial": historial})
    return respuesta.content