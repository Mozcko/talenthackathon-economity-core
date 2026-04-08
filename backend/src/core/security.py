# src/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from typing import Dict, Any

from src.core.config import settings

# HTTPBearer le dice a FastAPI/Swagger que los endpoints requieren un token Bearer
token_auth_scheme = HTTPBearer()

# Lazy-initialized JWKS client (cached, fetches Clerk public keys automatically)
_jwks_client: PyJWKClient | None = None

def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(settings.clerk_jwks_url)
    return _jwks_client

def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> Dict[str, Any]:
    """
    Dependencia de FastAPI que intercepta el JWT emitido por Clerk,
    valida la firma criptográfica y retorna el payload.
    Soporta RS256 via JWKS (CLERK_JWKS_URL) o HS256 via JWT_SECRET_KEY.
    """
    token = credentials.credentials

    try:
        if settings.clerk_jwks_url:
            # RS256: obtiene la clave pública de Clerk automáticamente
            signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
        elif settings.jwt_secret_key:
            # HS256: clave simétrica (requiere que Clerk esté configurado para HS256)
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Auth no configurada: define CLERK_JWKS_URL o JWT_SECRET_KEY en .env",
            )

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