"""
LLM Parser Tests

Unit tests for LLM response parsing utilities
"""
import pytest
from backend.utils.llm_parser import (
    parse_llm_json_response,
    find_complete_json,
    normalize_response,
    get_fallback_suggestions
)


class TestParseLLMJsonResponse:
    """Tests for parse_llm_json_response function"""

    def test_empty_reply_returns_empty_response(self):
        """Empty input should return empty reply and suggestions"""
        result = parse_llm_json_response('')
        assert result == {'reply': '', 'suggestions': []}

    def test_none_reply_returns_empty_response(self):
        """None input should return empty reply and suggestions"""
        result = parse_llm_json_response(None)
        assert result == {'reply': '', 'suggestions': []}

    def test_direct_json_parse(self):
        """Valid JSON with reply field should be parsed directly"""
        json_input = '{"reply": "Hello world", "suggestions": ["Option 1", "Option 2"]}'
        result = parse_llm_json_response(json_input)
        assert result['reply'] == 'Hello world'
        assert len(result['suggestions']) == 2

    def test_json_in_code_block(self):
        """JSON wrapped in code block should be extracted"""
        input_text = '''Here is my response:
```json
{"reply": "Parsed from code block", "suggestions": ["Suggestion 1"]}
```
'''
        result = parse_llm_json_response(input_text)
        assert result['reply'] == 'Parsed from code block'
        assert len(result['suggestions']) == 1

    def test_json_in_generic_code_block(self):
        """JSON in generic code block (no language) should be extracted"""
        input_text = '''Response:
```
{"reply": "Generic code block", "suggestions": []}
```
'''
        result = parse_llm_json_response(input_text)
        assert result['reply'] == 'Generic code block'

    def test_json_embedded_in_text(self):
        """JSON embedded in surrounding text should be found"""
        input_text = 'Here is my analysis: {"reply": "Found in text", "suggestions": ["A"]} That was my answer.'
        result = parse_llm_json_response(input_text)
        assert result['reply'] == 'Found in text'

    def test_fallback_to_raw_text(self):
        """Non-JSON text should be returned as raw reply"""
        plain_text = "This is just a plain text response without any JSON."
        result = parse_llm_json_response(plain_text)
        assert result['reply'] == plain_text
        assert result['suggestions'] == []

    def test_malformed_json_fallback(self):
        """Malformed JSON should fallback to raw text"""
        malformed = '{"reply": "unclosed string'
        result = parse_llm_json_response(malformed)
        assert result['reply'] == malformed
        assert result['suggestions'] == []

    def test_json_without_reply_field(self):
        """JSON without 'reply' field should fallback to raw text"""
        no_reply = '{"message": "This has no reply field"}'
        result = parse_llm_json_response(no_reply)
        assert result['reply'] == no_reply

    def test_nested_json_object(self):
        """Nested JSON objects should be handled correctly"""
        nested = '{"reply": "Main response", "suggestions": ["A"], "metadata": {"key": "value"}}'
        result = parse_llm_json_response(nested)
        assert result['reply'] == 'Main response'


class TestFindCompleteJson:
    """Tests for find_complete_json function"""

    def test_simple_json_object(self):
        """Simple JSON object should be found completely"""
        text = '{"key": "value"}'
        result = find_complete_json(text, 0)
        assert result == '{"key": "value"}'

    def test_nested_braces(self):
        """Nested braces should be handled correctly"""
        text = '{"outer": {"inner": "value"}}'
        result = find_complete_json(text, 0)
        assert result == '{"outer": {"inner": "value"}}'

    def test_string_with_braces(self):
        """Braces inside strings should be ignored"""
        text = '{"message": "Hello {world}"}'
        result = find_complete_json(text, 0)
        assert result == '{"message": "Hello {world}"}'

    def test_escaped_quotes(self):
        """Escaped quotes in strings should be handled"""
        text = '{"message": "He said \\"hello\\""}'
        result = find_complete_json(text, 0)
        assert result == '{"message": "He said \\"hello\\""}'

    def test_json_with_prefix(self):
        """JSON after text prefix should be found from correct position"""
        text = 'Prefix text {"reply": "value"} suffix'
        start = text.find('{')
        result = find_complete_json(text, start)
        assert result == '{"reply": "value"}'

    def test_unclosed_json_returns_none(self):
        """Unclosed JSON should return None"""
        text = '{"key": "value"'
        result = find_complete_json(text, 0)
        assert result is None


class TestNormalizeResponse:
    """Tests for normalize_response function"""

    def test_string_suggestions_normalized(self):
        """String suggestions should be converted to objects"""
        result = normalize_response({
            'reply': 'Test',
            'suggestions': ['Option 1', 'Option 2']
        })
        assert result['suggestions'][0]['title'] == 'Option 1'
        assert result['suggestions'][0]['action'] == 'fill_input'
        assert result['suggestions'][0]['payload'] == 'Option 1'

    def test_dict_suggestions_preserved(self):
        """Dict suggestions should preserve their structure"""
        result = normalize_response({
            'reply': 'Test',
            'suggestions': [
                {'title': 'Custom', 'action': 'navigate', 'payload': '/path'}
            ]
        })
        assert result['suggestions'][0]['title'] == 'Custom'
        assert result['suggestions'][0]['action'] == 'navigate'
        assert result['suggestions'][0]['payload'] == '/path'

    def test_suggestions_limited_to_five(self):
        """Suggestions should be limited to 5 items"""
        result = normalize_response({
            'reply': 'Test',
            'suggestions': ['1', '2', '3', '4', '5', '6', '7']
        })
        assert len(result['suggestions']) == 5

    def test_non_list_suggestions_becomes_empty(self):
        """Non-list suggestions should become empty list"""
        result = normalize_response({
            'reply': 'Test',
            'suggestions': 'not a list'
        })
        assert result['suggestions'] == []

    def test_missing_reply_returns_empty_string(self):
        """Missing reply field should return empty string"""
        result = normalize_response({'suggestions': []})
        assert result['reply'] == ''

    def test_dict_suggestion_with_text_field(self):
        """Dict suggestion with 'text' instead of 'title' should work"""
        result = normalize_response({
            'reply': 'Test',
            'suggestions': [{'text': 'Alternative'}]
        })
        assert result['suggestions'][0]['title'] == 'Alternative'


class TestGetFallbackSuggestions:
    """Tests for get_fallback_suggestions function"""

    def test_returns_default_suggestions(self):
        """Should return default interview-related suggestions"""
        result = get_fallback_suggestions()
        assert len(result) == 3
        assert all('title' in s for s in result)
        assert all('action' in s for s in result)
        assert all('payload' in s for s in result)

    def test_with_none_context(self):
        """Should handle None context gracefully"""
        result = get_fallback_suggestions(None)
        assert len(result) == 3

    def test_with_empty_context(self):
        """Should handle empty context gracefully"""
        result = get_fallback_suggestions({})
        assert len(result) == 3

    def test_suggestions_have_fill_input_action(self):
        """All default suggestions should have fill_input action"""
        result = get_fallback_suggestions()
        assert all(s['action'] == 'fill_input' for s in result)


class TestAIExceptions:
    """Tests for AI exception classes"""

    def test_ai_service_error_to_dict(self):
        """AIServiceError should convert to dict properly"""
        from backend.utils.ai_exceptions import AIServiceError
        error = AIServiceError('Test message', 'TEST_CODE')
        result = error.to_dict()
        assert result['error']['code'] == 'TEST_CODE'
        assert result['error']['message'] == 'Test message'

    def test_ai_provider_not_configured(self):
        """AIProviderNotConfigured should have correct code"""
        from backend.utils.ai_exceptions import AIProviderNotConfigured
        error = AIProviderNotConfigured('OpenAI')
        assert error.code == 'AI_PROVIDER_NOT_CONFIGURED'
        assert 'OpenAI' in error.message

    def test_ai_auth_error(self):
        """AIAuthError should have correct code"""
        from backend.utils.ai_exceptions import AIAuthError
        error = AIAuthError('OpenAI')
        assert error.code == 'AI_AUTH_ERROR'
        assert 'authentication failed' in error.message.lower()

    def test_ai_timeout_error(self):
        """AITimeoutError should include timeout duration"""
        from backend.utils.ai_exceptions import AITimeoutError
        error = AITimeoutError(30)
        assert error.code == 'AI_TIMEOUT'
        assert '30' in error.message

    def test_ai_rate_limit_error(self):
        """AIRateLimitError should have correct code"""
        from backend.utils.ai_exceptions import AIRateLimitError
        error = AIRateLimitError('OpenAI')
        assert error.code == 'AI_RATE_LIMIT'
        assert 'rate limit' in error.message.lower()

    def test_ai_connection_error(self):
        """AIConnectionError should have correct code"""
        from backend.utils.ai_exceptions import AIConnectionError
        error = AIConnectionError('Ollama')
        assert error.code == 'AI_CONNECTION_ERROR'
        assert 'Ollama' in error.message
