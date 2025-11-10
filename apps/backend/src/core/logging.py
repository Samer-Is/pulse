"""
Structured logging configuration with trace_id support.
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict
import structlog
from pythonjsonlogger import jsonlogger

from .config import get_settings


# Context variable to store trace_id per request
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


def set_trace_id(trace_id: str = None) -> str:
    """Set trace_id for current context. Generate if not provided."""
    if not trace_id:
        trace_id = str(uuid.uuid4())
    trace_id_var.set(trace_id)
    return trace_id


def get_trace_id() -> str:
    """Get current trace_id from context."""
    return trace_id_var.get()


def add_trace_id(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    """Structlog processor to add trace_id to every log entry."""
    event_dict["trace_id"] = get_trace_id()
    return event_dict


def setup_logging():
    """Configure structured logging with JSON output."""
    settings = get_settings()
    
    # Configure standard library logging
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    if settings.LOG_FORMAT == "json":
        # JSON formatter for production
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s %(trace_id)s"
        )
        handler.setFormatter(formatter)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            handlers=[handler],
            force=True
        )
    else:
        # Human-readable format for development
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            stream=sys.stdout,
            force=True
        )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            add_trace_id,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json"
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__):
    """Get a configured logger instance."""
    return structlog.get_logger(name)
