"""
OpenAI Provider

Implementation for OpenAI GPT models.
"""
from typing import Generator, Dict, Any, List
from .base import AIProviderBase
from backend.utils.ai_exceptions import (
    AIProviderNotConfigured,
    AIAuthError,
    AITimeoutError,
    AIRateLimitError,
    AIConnectionError,
    AIServiceError
)


class OpenAIProvider(AIProviderBase):
    """OpenAI GPT provider implementation."""

    name = "openai"
    supports_streaming = True

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o-mini)
        """
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise AIProviderNotConfigured('OpenAI')
        return self._client

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Synchronous chat with OpenAI.

        Args:
            messages: Conversation messages
            **kwargs: Additional options (max_tokens, temperature, etc.)

        Returns:
            str: Assistant response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            self._handle_error(e)

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Streaming chat with OpenAI.

        Args:
            messages: Conversation messages
            **kwargs: Additional options

        Yields:
            str: Response chunks
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            self._handle_error(e)

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate OpenAI configuration."""
        api_key = config.get('api_key') or config.get('apiKey')
        if not api_key:
            raise ValueError("OpenAI API key is required")
        if not api_key.startswith('sk-'):
            raise ValueError("Invalid OpenAI API key format")
        return True

    def get_default_model(self) -> str:
        return "gpt-4o-mini"

    def list_models(self) -> List[str]:
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]

    def _handle_error(self, e: Exception):
        """Convert OpenAI exceptions to our exception types."""
        error_str = str(e).lower()

        if 'authentication' in error_str or 'api key' in error_str or 'unauthorized' in error_str:
            raise AIAuthError('OpenAI')
        elif 'rate limit' in error_str or 'too many requests' in error_str:
            raise AIRateLimitError('OpenAI')
        elif 'timeout' in error_str:
            raise AITimeoutError()
        elif 'connection' in error_str:
            raise AIConnectionError('OpenAI')
        else:
            raise AIServiceError(f'OpenAI API error: {str(e)}', 'AI_API_ERROR')
