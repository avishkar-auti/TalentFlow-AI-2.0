from fastapi.middleware.cors import CORSMiddleware
from typing import Tuple, Dict, Any

def get_cors_middleware(origins_str: str) -> Tuple[type, Dict[str, Any]]:
    """
    Configure and return the CORS middleware.
    
    Args:
        origins_str: Comma-separated list of allowed origins.
    """
    origins = [origin.strip() for origin in origins_str.split(",")] if origins_str else []
    
    return (
        CORSMiddleware,
        {
            "allow_origins": origins,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    )
