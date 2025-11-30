"""
Provider Registry

Central registry for AI provider discovery and instantiation.
"""
from typing import Dict, Type, List, Optional
from .base import AIProviderBase


class ProviderRegistry:
    """
    Registry for AI providers.

    Allows dynamic registration and lookup of provider implementations.
    """

    _providers: Dict[str, Type[AIProviderBase]] = {}
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls):
        """Lazy load built-in providers."""
        if cls._initialized:
            return

        # Import and register built-in providers
        from .openai_provider import OpenAIProvider
        from .ollama_provider import OllamaProvider
        from .claude_provider import ClaudeProvider
        from .gemini_provider import GeminiProvider

        cls._providers = {
            'openai': OpenAIProvider,
            'ollama': OllamaProvider,
            'claude': ClaudeProvider,
            'gemini': GeminiProvider
        }
        cls._initialized = True

    @classmethod
    def get(cls, name: str) -> Type[AIProviderBase]:
        """
        Get provider class by name.

        Args:
            name: Provider name (openai, ollama, claude, gemini)

        Returns:
            Provider class

        Raises:
            ValueError: If provider not found
        """
        cls._ensure_initialized()

        if name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider: {name}. "
                f"Available providers: {available}"
            )
        return cls._providers[name]

    @classmethod
    def register(cls, name: str, provider_class: Type[AIProviderBase]):
        """
        Register a new provider.

        Args:
            name: Provider name
            provider_class: Provider class implementing AIProviderBase
        """
        cls._ensure_initialized()

        if not issubclass(provider_class, AIProviderBase):
            raise TypeError(
                f"Provider must be subclass of AIProviderBase, "
                f"got {type(provider_class)}"
            )
        cls._providers[name] = provider_class

    @classmethod
    def list_available(cls) -> List[str]:
        """
        List all available provider names.

        Returns:
            List of provider names
        """
        cls._ensure_initialized()
        return list(cls._providers.keys())

    @classmethod
    def create(
        cls,
        name: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> AIProviderBase:
        """
        Create a provider instance.

        Args:
            name: Provider name
            api_key: API key (if required by provider)
            model: Model name (optional, uses provider default)
            **kwargs: Additional provider-specific options

        Returns:
            Provider instance
        """
        provider_class = cls.get(name)

        # Build kwargs based on provider requirements
        init_kwargs = {}

        if name == 'ollama':
            # Ollama doesn't need API key
            if model:
                init_kwargs['model'] = model
            if 'endpoint' in kwargs:
                init_kwargs['endpoint'] = kwargs['endpoint']
        else:
            # Other providers need API key
            if api_key:
                init_kwargs['api_key'] = api_key
            if model:
                init_kwargs['model'] = model

        return provider_class(**init_kwargs)

    @classmethod
    def get_provider_info(cls, name: str) -> Dict:
        """
        Get information about a provider.

        Args:
            name: Provider name

        Returns:
            Dict with provider info (name, supports_streaming, models)
        """
        provider_class = cls.get(name)

        # Create temporary instance to get info
        temp_instance = None
        try:
            if name == 'ollama':
                temp_instance = provider_class()
            else:
                # Can't create without API key, just use class attributes
                pass
        except Exception:
            pass

        return {
            'name': provider_class.name,
            'supports_streaming': provider_class.supports_streaming,
            'requires_api_key': name != 'ollama',
            'models': temp_instance.list_models() if temp_instance else []
        }
