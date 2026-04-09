# src/services/ai/multimodal_parser.py
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from decimal import Decimal
import base64

from src.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)

class TransaccionExtraida(BaseModel):
    monto: Decimal = Field(description="El monto numérico exacto de la operación, siempre positivo.")
    descripcion: str = Field(description="Una breve descripción limpia de la transacción.")
    es_ingreso: bool = Field(description="True solo si es un ingreso (sueldo, venta, transferencia recibida). False para cualquier gasto, pago o compra.")
    categoria_sugerida: str = Field(description="Categoría del movimiento (ej. 'Gasolina', 'Sueldo/Nómina', 'Despensa/Super', 'Renta', 'Restaurante').")

def transcribir_audio(audio_path: str) -> str:
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcription.text

def extraer_datos_financieros(texto: str) -> TransaccionExtraida:
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(TransaccionExtraida)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Eres el motor de extracción de Economity. "
         "Extrae los datos financieros del texto. "
         "REGLA: es_ingreso=True SOLO para salarios, ventas o transferencias recibidas. "
         "es_ingreso=False para TODO gasto, pago, compra o servicio contratado."),
        ("human", "Texto: {texto}")
    ])
    
    chain = prompt | structured_llm
    return chain.invoke({"texto": texto})

def extraer_datos_de_imagen(image_path: str) -> TransaccionExtraida:
    """Lee un ticket fotografiado y extrae los datos usando GPT-4o Vision."""
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(TransaccionExtraida)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres Economity. Extrae los datos financieros de la imagen proporcionada."),
        ("human", [
            {"type": "text", "text": "Este es un ticket o recibo de compra — es siempre un GASTO (es_ingreso=False). Extrae el monto total y la categoría del gasto:"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ])
    ])
    
    chain = prompt | structured_llm
    return chain.invoke({})