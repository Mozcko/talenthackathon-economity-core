# src/services/ai/router.py
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from src.core.config import settings

async def clasificar_intencion_async(pregunta: str) -> str:
    """
    Actúa como el 'Agent Router' del diagrama de Economity.
    Decide qué flujo especializado debe atender la petición.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini", # Rápido y barato para enrutamiento
        temperature=0, 
        api_key=settings.openai_api_key
    )

    template = """
    Eres el Supervisor de Economity, un arquitecto financiero autónomo.
    Clasifica la intención del usuario en UNA sola categoría:
    
    - CONSULTA_FISCAL: Preguntas sobre impuestos, ISR, exenciones, SOFIPOS, CETES o regulaciones. (Requiere RAG).
    - PROYECCION_MATEMATICA: El usuario pide calcular rendimientos, interés compuesto, o proyectar inversiones a futuro. (Requiere Tool Calling).
    - GENERAL: Saludos, educación financiera básica o charla general.

    Responde ÚNICAMENTE con la palabra de la categoría.
    Mensaje: {pregunta}
    Categoría:"""
    
    cadena = PromptTemplate.from_template(template) | llm
    
    respuesta = await cadena.ainvoke({"pregunta": pregunta})
    return respuesta.content.strip()