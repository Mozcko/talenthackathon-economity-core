from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    app_title: str = "Economity API"
    app_description: str = "Backend Core MVP para el Hackathon"
    app_version: str = "1.0.0"

    # Database Settings
    database_url: str
    
    # Vector Database Settings (Opcional, con valor por defecto)
    chroma_url: str = "http://localhost:8001"
    
    # Auth Settings - provide either clerk_jwks_url (preferred) or jwt_secret_key
    clerk_jwks_url: Optional[str] = None
    jwt_secret_key: Optional[str] = None

    # LLM API Keys
    openai_api_key: str
    # Hacemos DeepSeek y Claude opcionales por si no los usan en todos los flujos del MVP
    deepseek_api_key: Optional[str] = None
    claudecode_api_key: Optional[str] = None

    @field_validator('clerk_jwks_url', 'jwt_secret_key', mode='before')
    @classmethod
    def strip_quotes(cls, v):
        if isinstance(v, str):
            return v.strip('"\'')
        return v

    # Pydantic v2: Configuración para leer el archivo .env
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # Ignora variables extras en el .env que no estén en esta clase
    )

# Instanciamos la clase (Singleton) para importarla en otros archivos
settings = Settings()