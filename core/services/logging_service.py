"""
Logging Service for NIS HUB

Provides structured logging with rich formatting for the entire NIS HUB system.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import structlog
from rich.logging import RichHandler
from rich.console import Console
from rich.text import Text

# Create logs directory if it doesn't exist
LOGS_DIR = Path("../logs")
LOGS_DIR.mkdir(exist_ok=True)

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Set up structured logging for the NIS HUB system.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    
    Returns:
        Configured structured logger
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                console=Console(stderr=True),
                show_time=True,
                show_path=True
            )
        ],
        level=getattr(logging, log_level.upper())
    )
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        logging.getLogger().addHandler(file_handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            )
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Create and return the main logger
    logger = structlog.get_logger("nis_hub_core")
    logger.info("🔧 Logging system initialized", level=log_level, file=log_file)
    
    return logger

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a named logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        Named logger instance
    """
    return structlog.get_logger(name)

def log_system_event(logger: structlog.stdlib.BoundLogger, event_type: str, **kwargs):
    """
    Log a system event with consistent formatting.
    
    Args:
        logger: Logger instance
        event_type: Type of system event
        **kwargs: Additional event data
    """
    logger.info(
        f"🔄 System Event: {event_type}",
        event_type=event_type,
        **kwargs
    )

def log_node_activity(logger: structlog.stdlib.BoundLogger, node_id: str, action: str, **kwargs):
    """
    Log node activity with consistent formatting.
    
    Args:
        logger: Logger instance
        node_id: Node identifier
        action: Action performed
        **kwargs: Additional activity data
    """
    logger.info(
        f"🤖 Node Activity: {action}",
        node_id=node_id,
        action=action,
        **kwargs
    )

def log_memory_operation(logger: structlog.stdlib.BoundLogger, operation: str, **kwargs):
    """
    Log memory operation with consistent formatting.
    
    Args:
        logger: Logger instance
        operation: Memory operation type
        **kwargs: Additional operation data
    """
    logger.info(
        f"🧠 Memory Operation: {operation}",
        operation=operation,
        **kwargs
    )

def log_mission_event(logger: structlog.stdlib.BoundLogger, mission_id: str, event: str, **kwargs):
    """
    Log mission event with consistent formatting.
    
    Args:
        logger: Logger instance
        mission_id: Mission identifier
        event: Event type
        **kwargs: Additional event data
    """
    logger.info(
        f"🎯 Mission Event: {event}",
        mission_id=mission_id,
        event=event,
        **kwargs
    )

def log_error(logger: structlog.stdlib.BoundLogger, error: Exception, context: str, **kwargs):
    """
    Log error with consistent formatting and context.
    
    Args:
        logger: Logger instance
        error: Exception instance
        context: Error context description
        **kwargs: Additional error data
    """
    logger.error(
        f"❌ Error in {context}: {str(error)}",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context,
        **kwargs,
        exc_info=True
    )

def log_performance_metric(logger: structlog.stdlib.BoundLogger, metric_name: str, value: float, unit: str = "", **kwargs):
    """
    Log performance metric with consistent formatting.
    
    Args:
        logger: Logger instance
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        **kwargs: Additional metric data
    """
    logger.info(
        f"📊 Performance Metric: {metric_name}",
        metric_name=metric_name,
        value=value,
        unit=unit,
        **kwargs
    )

class NISHubLogger:
    """
    Specialized logger class for NIS HUB with context management.
    """
    
    def __init__(self, component: str):
        """
        Initialize component-specific logger.
        
        Args:
            component: Component name for logging context
        """
        self.component = component
        self.logger = get_logger(component)
        self.logger = self.logger.bind(component=component)
    
    def system_startup(self, **kwargs):
        """Log system startup event."""
        self.logger.info(f"🚀 {self.component} starting up", **kwargs)
    
    def system_shutdown(self, **kwargs):
        """Log system shutdown event."""
        self.logger.info(f"🔄 {self.component} shutting down", **kwargs)
    
    def api_request(self, method: str, endpoint: str, **kwargs):
        """Log API request."""
        self.logger.info(f"🌐 API Request: {method} {endpoint}", method=method, endpoint=endpoint, **kwargs)
    
    def api_response(self, status_code: int, endpoint: str, duration_ms: float, **kwargs):
        """Log API response."""
        self.logger.info(
            f"📤 API Response: {status_code}",
            status_code=status_code,
            endpoint=endpoint,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def websocket_connection(self, action: str, client_id: str, **kwargs):
        """Log WebSocket connection events."""
        self.logger.info(f"🔌 WebSocket {action}: {client_id}", action=action, client_id=client_id, **kwargs)
    
    def data_operation(self, operation: str, table: str, count: int = None, **kwargs):
        """Log data operation."""
        message = f"💾 Data Operation: {operation} on {table}"
        if count is not None:
            message += f" ({count} records)"
        self.logger.info(message, operation=operation, table=table, count=count, **kwargs)
    
    def security_event(self, event_type: str, **kwargs):
        """Log security-related events."""
        self.logger.warning(f"🔐 Security Event: {event_type}", event_type=event_type, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(f"🔍 {message}", **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(f"ℹ️ {message}", **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(f"⚠️ {message}", **kwargs)
    
    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error message."""
        if error:
            self.logger.error(f"❌ {message}: {str(error)}", error_type=type(error).__name__, **kwargs, exc_info=True)
        else:
            self.logger.error(f"❌ {message}", **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(f"🚨 {message}", **kwargs) 