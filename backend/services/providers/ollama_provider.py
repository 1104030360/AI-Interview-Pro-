"""
Ollama Provider

Implementation for local Ollama models.
"""
import requests
from typing import Generator, Dict, Any, List
from .base import AIProviderBase
from backend.utils.ai_exceptions import (
    AITimeoutError,
    AIConnectionError,
    AIServiceError
)


class OllamaProvider(AIProviderBase):
    """Ollama local LLM provider implementation."""

    name = "ollama"
    supports_streaming = True

    def __init__(
        self,
        model: str = "llama3:latest",
        endpoint: str = "http://localhost:11434"
    ):
        """
        Initialize Ollama provider.

        Args:
            model: Model to use (default: llama3:latest)
            endpoint: Ollama API endpoint (default: localhost:11434)
        """
        self.model = model
        self.endpoint = endpoint.rstrip('/')
        self.timeout = 120  # Longer timeout for local models

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Synchronous chat with Ollama.

        Args:
            messages: Conversation messages
            **kwargs: Additional options

        Returns:
            str: Assistant response
        """
        try:
            response = requests.post(
                f"{self.endpoint}/api/chat",
                json={
                    'model': self.model,
                    'messages': messages,
                    'stream': False
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get('message', {}).get('content', '')

        except requests.exceptions.Timeout:
            raise AITimeoutError(self.timeout)
        except requests.exceptions.ConnectionError:
            raise AIConnectionError('Ollama')
        except requests.exceptions.RequestException as e:
            raise AIServiceError(f'Ollama API error: {str(e)}', 'AI_API_ERROR')

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Streaming chat with Ollama.

        Args:
            messages: Conversation messages
            **kwargs: Additional options

        Yields:
            str: Response chunks
        """
        try:
            response = requests.post(
                f"{self.endpoint}/api/chat",
                json={
                    'model': self.model,
                    'messages': messages,
                    'stream': True
                },
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()

            import json
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        content = data.get('message', {}).get('content', '')
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.Timeout:
            raise AITimeoutError(self.timeout)
        except requests.exceptions.ConnectionError:
            raise AIConnectionError('Ollama')
        except requests.exceptions.RequestException as e:
            raise AIServiceError(f'Ollama API error: {str(e)}', 'AI_API_ERROR')

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Ollama configuration."""
        # Ollama doesn't require API key, just needs to be running
        endpoint = config.get('endpoint', 'http://localhost:11434')
        try:
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            raise ValueError(
                f"Cannot connect to Ollama at {endpoint}. "
                "Please ensure Ollama is running."
            )

    def get_default_model(self) -> str:
        return "llama3:latest"

    def list_models(self) -> List[str]:
        """List models available on the Ollama server."""
        try:
            response = requests.get(
                f"{self.endpoint}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return [m['name'] for m in data.get('models', [])]
        except requests.exceptions.RequestException:
            pass
        return ["llama3:latest", "llama2:latest", "mistral:latest"]
