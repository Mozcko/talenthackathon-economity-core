import base64
import mimetypes
import re
import openai
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.core.config import settings

# Usamos el cliente asíncrono nativo de OpenAI para Whisper
client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

# Palabras clave que indican inequívocamente gasto o ingreso.
# Se aplican DESPUÉS de que el LLM extrae los demás campos, anulando su clasificación.
_KEYWORDS_GASTO = re.compile(
    r"\b(gast[eéó]|pagu[eé]|pag[oó]|compr[eéó]|deb[oóí]|cost[oó]|sal[ií][oó]|gasto)\b",
    re.IGNORECASE,
)
_KEYWORDS_INGRESO = re.compile(
    r"\b(gan[eéó]|cobr[eéó]|recib[ií]|ingres[eéó]|deposit[oóa]|vend[ií]|me\s+pag[ao]ron|me\s+deposit[ao]ron)\b",
    re.IGNORECASE,
)


def _override_es_ingreso(texto: str, datos: dict) -> dict:
    """Fuerza es_ingreso basado en palabras clave; el LLM solo decide si no hay señal clara."""
    if _KEYWORDS_GASTO.search(texto):
        datos["es_ingreso"] = False
    elif _KEYWORDS_INGRESO.search(texto):
        datos["es_ingreso"] = True
    return datos

class DatosExtraidos(BaseModel):
    """Esquema estricto que la IA debe respetar al responder"""
    monto: float = Field(description="El monto de la transacción (siempre positivo, ej: 150.50)")
    descripcion: str = Field(description="Descripción clara y concisa (ej. 'Casino', 'Uber', 'Nómina')")
    es_ingreso: bool = Field(description="True SOLO si es un ingreso explícito: sueldo, nómina, venta, transferencia recibida, cobro. False para TODO lo demás: compras, pagos, servicios, gasolina, comida, entretenimiento, etc.")
    categoria_sugerida: str = Field(description="Categoría conductual (ej. 'Apuestas/Casino', 'Antros/Fiesta', 'Despensa/Super', 'Sueldo/Nómina')")
    es_riesgoso: bool = Field(description="True si el gasto es impulsivo o de riesgo (apuestas, juegos, fiesta, suscripciones)")

async def extraer_datos_texto_async(texto: str) -> dict:
    """Analiza texto plano para extraer la transacción estructurada bajo el lente conductual."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=settings.openai_api_key)
    estructurador = llm.with_structured_output(DatosExtraidos)
    
    prompt = (
        "Analiza el siguiente texto y extrae la transacción financiera.\n"
        "REGLA CRÍTICA es_ingreso: es_ingreso=True SOLO si el texto describe dinero RECIBIDO (sueldo, nómina, venta, cobro, transferencia recibida). "
        "es_ingreso=False para CUALQUIER pago, compra, gasto, servicio, gasolina, comida, renta, o consumo. En caso de duda, usa False.\n"
        "REGLA CONDUCTUAL: Clasifica como 'es_riesgoso=True' cualquier gasto en apuestas, casinos, "
        "compras impulsivas en juegos (skins, gemas), alcohol, antros o gastos innecesarios.\n"
        f"Texto: {texto}"
    )
    resultado = await estructurador.ainvoke(prompt)
    
    datos = resultado.model_dump()
    datos["texto_original"] = texto
    return _override_es_ingreso(texto, datos)

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
            {"type": "text", "text": "Analiza este ticket, recibo o factura. REGLA: un ticket o recibo es SIEMPRE un gasto (es_ingreso=False). Extrae el monto TOTAL pagado, una descripción breve de la compra y sugiere una categoría."},
            {"type": "image_url", "image_url": {"url": f"data:{mimetypes.guess_type(file_path)[0] or 'image/jpeg'};base64,{base64_image}"}}
        ]
    )
    resultado = await estructurador.ainvoke([mensaje])
    
    datos = resultado.model_dump()
    datos["texto_original"] = "Imagen de recibo procesada"
    datos["es_ingreso"] = False  # un ticket/recibo es siempre un gasto
    return datos