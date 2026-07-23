import logging
import sys
from logging.handlers import RotatingFileHandler
import structlog
from pathlib import Path
from contextvars import ContextVar
from typing import Any, MutableMapping
from .config import settings
import re

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# Ensure logs directory exists
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def redact_pii(logger: logging.Logger, log_method: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """Redact sensitive PII data from logs."""
    for key in event_dict:
        if isinstance(event_dict[key], str):
            # Simple email redaction
            event_dict[key] = re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED_EMAIL]', event_dict[key])
    return event_dict

def add_request_id(logger: logging.Logger, log_method: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """Add request ID to log events."""
    req_id = request_id_var.get()
    if req_id:
        event_dict["request_id"] = req_id
    return event_dict

def setup_logger(name: str, log_file: str) -> structlog.BoundLogger:
    """Setup and configure a structlog logger."""
    
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure stdlib logging
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate logs if calling setup_logger multiple times
    if not logger.handlers:
        # File handler with rotation
        file_handler = RotatingFileHandler(
            LOGS_DIR / log_file,
            maxBytes=10 * 1024 * 1024, # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Formatter for stdlib handlers
        if settings.environment == "production":
            formatter = structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer()
            )
        else:
            formatter = structlog.stdlib.ProcessorFormatter(
                processor=structlog.dev.ConsoleRenderer()
            )
            
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            add_request_id,
            redact_pii,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger(name)


api_logger = setup_logger("api", "api.log")
agents_logger = setup_logger("agents", "agents.log")
firebase_logger = setup_logger("firebase", "firebase.log")
errors_logger = setup_logger("errors", "errors.log")
