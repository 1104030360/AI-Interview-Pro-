"""
Gemini Provider

Implementation for Google Gemini models.
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


class GeminiProvider(AIProviderBase):
    """Google Gemini provider implementation."""

    name = "gemini"
    supports_streaming = True

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google AI API key
            model: Model to use (default: gemini-1.5-flash)
        """
        self.api_key = api_key
        self.model_name = model
        self._model = None

    @property
    def model(self):
        """Lazy load Gemini model."""
        if self._model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
            except ImportError:
                raise AIProviderNotConfigured('Gemini (google-generativeai package not installed)')
        return self._model

    def _convert_messages(
        self,
        messages: List[Dict[str, str]]
    ) -> tuple:
        """
        Convert OpenAI-style messages to Gemini format.

        Returns:
            tuple: (history, last_message)
        """
        history = []
        system_prompt = ""

        for msg in messages[:-1]:
            if msg['role'] == 'system':
                system_prompt += msg['content'] + '\n\n'
            else:
                role = 'model' if msg['role'] == 'assistant' else 'user'
                history.append({
                    'role': role,
                    'parts': [msg['content']]
                })

        # Add system prompt to first user message if present
        last_message = messages[-1]['content']
        if system_prompt and messages[-1]['role'] == 'user':
            last_message = f"{system_prompt.strip()}\n\n{last_message}"

        return history, last_message

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Synchronous chat with Gemini.

        Args:
            messages: Conversation messages
            **kwargs: Additional options

        Returns:
            str: Assistant response
        """
        try:
            history, last_message = self._convert_messages(messages)

            chat = self.model.start_chat(history=history)
            response = chat.send_message(last_message)
            return response.text

        except Exception as e:
            self._handle_error(e)

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Streaming chat with Gemini.

        Args:
            messages: Conversation messages
            **kwargs: Additional options

        Yields:
            str: Response chunks
        """
        try:
            history, last_message = self._convert_messages(messages)

            chat = self.model.start_chat(history=history)
            response = chat.send_message(last_message, stream=True)

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            self._handle_error(e)

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Gemini configuration."""
        api_key = config.get('api_key') or config.get('apiKey')
        if not api_key:
            raise ValueError("Google AI API key is required")
        # Google API keys have various formats, just check it exists
        if len(api_key) < 20:
            raise ValueError("Invalid Google AI API key format")
        return True

    def get_default_model(self) -> str:
        return "gemini-1.5-flash"

    def list_models(self) -> List[str]:
        return [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro"
        ]

    def _handle_error(self, e: Exception):
        """Convert Gemini exceptions to our exception types."""
        error_str = str(e).lower()

        if 'api key' in error_str or 'invalid' in error_str or 'permission' in error_str:
            raise AIAuthError('Gemini')
        elif 'quota' in error_str or 'rate' in error_str:
            raise AIRateLimitError('Gemini')
        elif 'timeout' in error_str or 'deadline' in error_str:
            raise AITimeoutError()
        elif 'connection' in error_str or 'network' in error_str:
            raise AIConnectionError('Gemini')
        else:
            raise AIServiceError(f'Gemini API error: {str(e)}', 'AI_API_ERROR')
