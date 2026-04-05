# src/services/ai/memory.py
from typing import List, Dict

def formatear_historial(historial: List[Dict[str, str]], limite: int = 4) -> str:
    """
    Convierte el historial de mensajes del frontend en contexto de texto.
    """
    if not historial:
        return "Sin contexto previo."
    
    texto_historial = ""
    for msg in historial[-limite:]:
        rol = msg.get("rol", "Usuario")
        content = msg.get("content", "")
        texto_historial += f"{rol}: {content}\n"
        
    return texto_historial