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
    monto: Decimal = Field(description="El monto numérico exacto de la operación.")
    descripcion: str = Field(description="Una breve descripción limpia de la transacción.")
    sub_categoria_id: int = Field(description="Clasifica el gasto. 1: Ingreso, 2: Comida, 3: Transporte, 4: Otros.")

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
        ("system", "Eres el cerebro de Economity. Extrae los datos financieros clave en formato estructurado."),
        ("human", "Texto transcrito: {texto}")
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
            {"type": "text", "text": "Analiza este ticket y extrae el monto total y de qué trata el gasto:"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ])
    ])
    
    chain = prompt | structured_llm
    return chain.invoke({})