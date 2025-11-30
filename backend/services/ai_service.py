"""
AI Service

Business logic for LLM integration using pluggable provider architecture.
"""
import logging
from typing import Dict, Any, List, Generator, Optional
from backend.services.settings_service import SettingsService
from backend.services.providers import ProviderRegistry, AIProviderBase
from backend.utils.llm_parser import parse_llm_json_response, get_fallback_suggestions
from backend.utils.ai_exceptions import (
    AIServiceError,
    AIProviderNotConfigured
)

logger = logging.getLogger(__name__)


class AIService:
    """Handle AI operations (chat, question generation) using provider registry."""

    def __init__(self, provider: AIProviderBase, prompts: Dict[str, str] = None):
        """
        Initialize AI service with a specific provider.

        Args:
            provider: AIProviderBase instance
            prompts: User prompts configuration
        """
        self.provider = provider
        self.prompts = prompts or {}

    @classmethod
    def for_user(cls, user_id: str) -> 'AIService':
        """
        Factory method to create AIService for a specific user.

        Args:
            user_id: User UUID string

        Returns:
            AIService instance configured with user's provider settings
        """
        settings = SettingsService.get_user_settings(user_id)
        ai_config = settings['ai']
        prompts = settings['prompts']

        provider_name = ai_config.get('provider', 'openai')
        api_key = ai_config.get('apiKey', '')
        model = ai_config.get('model', '')

        # Check if provider is valid
        available = ProviderRegistry.list_available()
        if provider_name not in available:
            raise ValueError(f'Unsupported AI provider: {provider_name}')

        # Check if provider requires API key
        if provider_name != 'ollama' and not api_key:
            raise AIProviderNotConfigured(provider_name)

        # Create provider instance
        provider = ProviderRegistry.create(
            name=provider_name,
            api_key=api_key,
            model=model if model else None
        )

        return cls(provider=provider, prompts=prompts)

    def _build_messages(
        self,
        message: str,
        context: Dict = None,
        prompt_key: str = 'coachChat'
    ) -> List[Dict[str, str]]:
        """
        Build message list for chat.

        Args:
            message: User message
            context: Conversation context with history
            prompt_key: Key in prompts dict for system prompt

        Returns:
            List of message dicts
        """
        # Build system prompt
        global_prompt = self.prompts.get('global', '')
        specific_prompt = self.prompts.get(
            prompt_key,
            'You are a helpful interview coach.'
        )
        system_prompt = f"{global_prompt}\n\n{specific_prompt}".strip()

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add conversation history
        if context and 'history' in context and context['history']:
            messages.extend(context['history'])

        messages.append({"role": "user", "content": message})

        return messages

    def chat(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """
        Chat with AI coach.

        Args:
            message: User message content
            context: Optional conversation context

        Returns:
            dict: {conversationId, reply, suggestions}
        """
        if context is None:
            context = {}

        messages = self._build_messages(message, context)

        # Call provider
        reply = self.provider.chat(messages)

        # Parse structured response
        parsed = parse_llm_json_response(reply)

        return {
            'conversationId': context.get('conversationId', 'new-conversation'),
            'reply': parsed.get('reply', reply),
            'suggestions': parsed.get('suggestions') or get_fallback_suggestions(context)
        }

    def chat_stream(
        self,
        message: str,
        context: Dict = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Streaming chat with AI coach.

        Args:
            message: User message content
            context: Optional conversation context

        Yields:
            dict: {content, done, full_response (when done)}
        """
        if context is None:
            context = {}

        messages = self._build_messages(message, context)

        if not self.provider.supports_streaming:
            # Fallback to non-streaming
            response = self.provider.chat(messages)
            yield {
                'content': response,
                'done': True,
                'full_response': response
            }
            return

        # Stream response
        full_response = ""
        for chunk in self.provider.chat_stream(messages):
            full_response += chunk
            yield {
                'content': chunk,
                'done': False
            }

        # Final message with complete response
        yield {
            'content': '',
            'done': True,
            'full_response': full_response
        }

    # Legacy static methods for backward compatibility

    @staticmethod
    def chat_legacy(
        user_id: str,
        message: str,
        context: dict = None
    ) -> Dict[str, Any]:
        """
        Legacy chat method (static, backward compatible).

        Deprecated: Use AIService.for_user(user_id).chat() instead.
        """
        service = AIService.for_user(user_id)
        return service.chat(message, context)

    @staticmethod
    def generate_questions(user_id: str, criteria: dict) -> List[Dict[str, Any]]:
        """
        Generate interview questions using AI.

        Args:
            user_id: User UUID string
            criteria: Generation criteria {role, difficulty, type, count}

        Returns:
            list: Generated questions
        """
        service = AIService.for_user(user_id)

        role = criteria.get('role', 'Software Engineer')
        difficulty = criteria.get('difficulty', 'Mid')
        q_type = criteria.get('type', 'Technical')
        count = criteria.get('count', 5)

        generation_prompt = f"""Generate {count} {difficulty} level {q_type} interview questions for a {role} position.

For each question, provide:
1. The question text
2. Expected topics/tags (as array)
3. Brief example answer outline

Format the response as a JSON array of objects with fields: text, tags, exampleAnswer.
"""

        response = service.chat(generation_prompt, {})

        # Parse response
        try:
            import json
            reply = response['reply']

            # Extract JSON from markdown code blocks
            if '```json' in reply:
                json_start = reply.find('```json') + 7
                json_end = reply.find('```', json_start)
                reply = reply[json_start:json_end].strip()
            elif '```' in reply:
                json_start = reply.find('```') + 3
                json_end = reply.find('```', json_start)
                reply = reply[json_start:json_end].strip()

            questions = json.loads(reply)

            # Add metadata
            for q in questions:
                q['type'] = q_type
                q['difficulty'] = difficulty
                q['role'] = role

            return questions

        except Exception as e:
            raise AIServiceError(
                f'Failed to parse generated questions: {str(e)}',
                'AI_PARSE_ERROR'
            )


# Alias for backward compatibility
def chat(user_id: str, message: str, context: dict = None) -> Dict[str, Any]:
    """Backward compatible function."""
    return AIService.chat_legacy(user_id, message, context)
