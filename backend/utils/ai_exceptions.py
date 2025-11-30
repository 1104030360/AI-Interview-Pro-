"""
AI Service Exceptions

Custom exceptions for AI service operations
"""


class AIServiceError(Exception):
    """Base exception for AI service errors"""

    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            'error': {
                'code': self.code,
                'message': self.message
            }
        }


class AIProviderNotConfigured(AIServiceError):
    """Raised when AI provider is not properly configured"""

    def __init__(self, provider: str = None):
        message = "AI provider not configured. Please set up your AI service in Settings."
        if provider:
            message = f"{provider} is not configured. Please add your API key in Settings."
        super().__init__(message, "AI_PROVIDER_NOT_CONFIGURED")


class AIAuthError(AIServiceError):
    """Raised when API key authentication fails"""

    def __init__(self, provider: str):
        super().__init__(
            f"{provider} authentication failed. Please check your API key in Settings.",
            "AI_AUTH_ERROR"
        )


class AITimeoutError(AIServiceError):
    """Raised when AI service times out"""

    def __init__(self, timeout_seconds: int = 60):
        super().__init__(
            f"AI service timed out after {timeout_seconds} seconds. Please try again.",
            "AI_TIMEOUT"
        )


class AIRateLimitError(AIServiceError):
    """Raised when rate limit is exceeded"""

    def __init__(self, provider: str = None):
        message = "Rate limit exceeded. Please wait a moment before trying again."
        if provider:
            message = f"{provider} rate limit exceeded. Please wait before trying again."
        super().__init__(message, "AI_RATE_LIMIT")


class AIConnectionError(AIServiceError):
    """Raised when unable to connect to AI service"""

    def __init__(self, provider: str):
        super().__init__(
            f"Unable to connect to {provider}. Please check your network connection.",
            "AI_CONNECTION_ERROR"
        )
