"""
AI Provider Base Class

Abstract base class defining the interface for all AI providers.
"""
from abc import ABC, abstractmethod
from typing import Generator, Dict, Any, List, Optional


class AIProviderBase(ABC):
    """
    Abstract base class for AI providers.

    All providers must implement chat() and optionally chat_stream().
    """

    name: str = ""
    supports_streaming: bool = False

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Synchronous chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Roles: 'system', 'user', 'assistant'
            **kwargs: Provider-specific options (max_tokens, temperature, etc.)

        Returns:
            str: The assistant's response content

        Raises:
            Various AI exceptions from ai_exceptions.py
        """
        pass

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Streaming chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Provider-specific options

        Yields:
            str: Chunks of the assistant's response

        Note:
            Default implementation falls back to non-streaming chat.
            Override in providers that support streaming.
        """
        # Default fallback: return full response as single chunk
        response = self.chat(messages, **kwargs)
        yield response

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate provider configuration.

        Args:
            config: Configuration dict (api_key, model, etc.)

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If configuration is invalid with details
        """
        pass

    def get_default_model(self) -> str:
        """Get the default model for this provider."""
        return ""

    def list_models(self) -> List[str]:
        """List available models for this provider."""
        return []
