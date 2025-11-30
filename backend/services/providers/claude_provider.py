"""
Claude Provider

Implementation for Anthropic Claude models.
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


class ClaudeProvider(AIProviderBase):
    """Anthropic Claude provider implementation."""

    name = "claude"
    supports_streaming = True

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-sonnet)
        """
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise AIProviderNotConfigured('Claude (anthropic package not installed)')
        return self._client

    def _convert_messages(
        self,
        messages: List[Dict[str, str]]
    ) -> tuple:
        """
        Convert OpenAI-style messages to Anthropic format.

        Returns:
            tuple: (system_message, chat_messages)
        """
        system_msg = None
        chat_messages = []

        for msg in messages:
            if msg['role'] == 'system':
                # Combine system messages
                if system_msg:
                    system_msg += '\n\n' + msg['content']
                else:
                    system_msg = msg['content']
            else:
                chat_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })

        return system_msg, chat_messages

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Synchronous chat with Claude.

        Args:
            messages: Conversation messages
            **kwargs: Additional options (max_tokens, etc.)

        Returns:
            str: Assistant response
        """
        try:
            system_msg, chat_messages = self._convert_messages(messages)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 4096),
                system=system_msg,
                messages=chat_messages
            )
            return response.content[0].text

        except Exception as e:
            self._handle_error(e)

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Streaming chat with Claude.

        Args:
            messages: Conversation messages
            **kwargs: Additional options

        Yields:
            str: Response chunks
        """
        try:
            system_msg, chat_messages = self._convert_messages(messages)

            with self.client.messages.stream(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 4096),
                system=system_msg,
                messages=chat_messages
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            self._handle_error(e)

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Claude configuration."""
        api_key = config.get('api_key') or config.get('apiKey')
        if not api_key:
            raise ValueError("Anthropic API key is required")
        if not api_key.startswith('sk-ant-'):
            raise ValueError("Invalid Anthropic API key format")
        return True

    def get_default_model(self) -> str:
        return "claude-3-sonnet-20240229"

    def list_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022"
        ]

    def _handle_error(self, e: Exception):
        """Convert Anthropic exceptions to our exception types."""
        error_str = str(e).lower()

        if 'authentication' in error_str or 'api key' in error_str or 'invalid' in error_str:
            raise AIAuthError('Claude')
        elif 'rate limit' in error_str or 'too many requests' in error_str:
            raise AIRateLimitError('Claude')
        elif 'timeout' in error_str:
            raise AITimeoutError()
        elif 'connection' in error_str:
            raise AIConnectionError('Claude')
        else:
            raise AIServiceError(f'Claude API error: {str(e)}', 'AI_API_ERROR')
