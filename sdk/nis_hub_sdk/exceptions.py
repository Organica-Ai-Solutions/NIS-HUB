"""
Exception classes for NIS HUB SDK.
"""


class NISHubError(Exception):
    """Base exception for all NIS HUB related errors."""
    pass


class ConnectionError(NISHubError):
    """Raised when connection to NIS HUB fails."""
    pass


class AuthenticationError(NISHubError):
    """Raised when authentication with NIS HUB fails."""
    pass


class RegistrationError(NISHubError):
    """Raised when node registration fails."""
    pass


class HeartbeatError(NISHubError):
    """Raised when heartbeat operations fail."""
    pass


class MemoryError(NISHubError):
    """Raised when memory operations fail."""
    pass


class MissionError(NISHubError):
    """Raised when mission operations fail."""
    pass


class ConfigurationError(NISHubError):
    """Raised when configuration is invalid."""
    pass


class ValidationError(NISHubError):
    """Raised when data validation fails."""
    pass 