import base64
import openai
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.core.config import settings

# Usamos el cliente asíncrono nativo de OpenAI para Whisper
client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

class DatosExtraidos(BaseModel):
    """Esquema estricto que la IA debe respetar al responder"""
    monto: float = Field(description="El monto de la transacción (siempre positivo, ej: 150.50)")
    descripcion: str = Field(description="Descripción clara y concisa (ej. 'Uber', 'Café', 'Nómina')")
    es_ingreso: bool = Field(description="True si es un ingreso/ganancia, False si es un gasto/compra")
    categoria_sugerida: str = Field(description="Nombre genérico de la categoría (ej. 'Alimentos', 'Transporte')")

async def extraer_datos_texto_async(texto: str) -> dict:
    """Analiza texto plano para extraer la transacción estructurada."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=settings.openai_api_key)
    estructurador = llm.with_structured_output(DatosExtraidos)
    
    prompt = f"Extrae los datos financieros de la siguiente oración o dictado:\n{texto}"
    resultado = await estructurador.ainvoke(prompt)
    
    datos = resultado.model_dump()
    datos["texto_original"] = texto
    return datos

async def extraer_datos_audio_async(file_path: str) -> dict:
    """Transcribe el audio usando Whisper y luego extrae los datos."""
    with open(file_path, "rb") as audio_file:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    # Reutilizamos el agente de texto ahora que tenemos la transcripción
    return await extraer_datos_texto_async(transcript.text)

async def extraer_datos_imagen_async(file_path: str) -> dict:
    """Analiza un ticket/recibo usando GPT-4o Vision para extraer el monto final."""
    with open(file_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
    # Usamos gpt-4o (la versión completa) porque soporta Visión
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)
    estructurador = llm.with_structured_output(DatosExtraidos)
    
    mensaje = HumanMessage(
        content=[
            {"type": "text", "text": "Analiza este ticket, recibo o factura. Extrae el monto TOTAL pagado, una descripción breve de la compra y sugiere una categoría."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
    )
    resultado = await estructurador.ainvoke([mensaje])
    
    datos = resultado.model_dump()
    datos["texto_original"] = "Imagen de recibo procesada"
    return datos