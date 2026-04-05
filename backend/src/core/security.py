# src/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict, Any

from src.core.config import settings

# HTTPBearer le dice a FastAPI/Swagger que los endpoints requieren un token Bearer
token_auth_scheme = HTTPBearer()

def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> Dict[str, Any]:
    """
    Dependencia de FastAPI que intercepta el JWT emitido por Clerk, 
    valida la firma criptográfica y retorna el payload.
    """
    token = credentials.credentials
    
    try:
        # Nota: En un entorno Clerk productivo real, se suelen usar claves asimétricas (RS256) 
        # y se consulta el JWKS endpoint de Clerk. Para tu MVP, usar la clave secreta o la PEM 
        # configurada en settings.jwt_secret_key funcionará perfectamente.
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=["HS256", "RS256"],
            options={"verify_aud": False} # Opcional: desactiva validación estricta de audiencia en MVP
        )
        
        # Clerk normalmente incluye el ID del usuario en el campo "sub"
        if "sub" not in payload:
            raise HTTPException(status_code=401, detail="Token no contiene identificador de usuario")
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token JWT ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firma criptográfica inválida: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_admin(token_payload: Dict[str, Any] = Depends(get_current_user_token)) -> Dict[str, Any]:
    """
    Dependencia que asegura que el usuario no solo esté autenticado, 
    sino que tenga el rol de 'admin'.
    """
    # Clerk permite agregar "public_metadata" a los usuarios. 
    # Dependiendo de cómo lo configures, puede venir en la raíz del payload o dentro de un objeto.
    rol = token_payload.get("org_role") or token_payload.get("role")
    
    # Para pruebas locales o si usas metadatos públicos de Clerk:
    # metadata = token_payload.get("public_metadata", {})
    # rol = metadata.get("role")

    if rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de administrador."
        )
    
    return token_payload