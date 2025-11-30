"""
LLM Response Parser

Multi-layer fallback parsing for LLM responses
"""
import json
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def parse_llm_json_response(reply: str) -> Dict[str, Any]:
    """
    Multi-layer fallback parsing for LLM response

    Attempts to parse structured JSON from LLM output, with fallbacks for
    various response formats.

    Args:
        reply: Raw LLM response string

    Returns:
        dict: {'reply': str, 'suggestions': list}
    """
    if not reply:
        return {'reply': '', 'suggestions': []}

    # Attempt 1: Direct JSON parse
    try:
        result = json.loads(reply.strip())
        if isinstance(result, dict) and 'reply' in result:
            return normalize_response(result)
    except json.JSONDecodeError:
        pass

    # Attempt 2: Extract from code block
    patterns = [
        r'```json\s*([\s\S]*?)```',
        r'```\s*([\s\S]*?)```',
    ]
    for pattern in patterns:
        match = re.search(pattern, reply)
        if match:
            try:
                result = json.loads(match.group(1).strip())
                if isinstance(result, dict) and 'reply' in result:
                    return normalize_response(result)
            except json.JSONDecodeError:
                continue

    # Attempt 3: Find JSON object in text
    json_match = re.search(r'\{[\s\S]*?"reply"[\s\S]*?\}', reply)
    if json_match:
        try:
            # Handle nested braces by finding the matching closing brace
            json_str = find_complete_json(reply, json_match.start())
            if json_str:
                result = json.loads(json_str)
                if isinstance(result, dict) and 'reply' in result:
                    return normalize_response(result)
        except json.JSONDecodeError:
            pass

    # Fallback: Use raw text as reply
    logger.debug("Failed to parse LLM response as JSON, using raw text")
    return {
        'reply': reply.strip(),
        'suggestions': []
    }


def find_complete_json(text: str, start: int) -> str:
    """Find complete JSON object starting at given position"""
    depth = 0
    in_string = False
    escape_next = False

    for i, char in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]

    return None


def normalize_response(result: dict) -> Dict[str, Any]:
    """Normalize parsed response to expected format"""
    suggestions = result.get('suggestions', [])

    # Ensure suggestions is a list
    if not isinstance(suggestions, list):
        suggestions = []

    # Limit to 5 suggestions
    suggestions = suggestions[:5]

    # Normalize suggestion format
    normalized_suggestions = []
    for s in suggestions:
        if isinstance(s, str):
            normalized_suggestions.append({
                'title': s,
                'action': 'fill_input',
                'payload': s
            })
        elif isinstance(s, dict):
            normalized_suggestions.append({
                'title': s.get('title', s.get('text', '')),
                'action': s.get('action', 'fill_input'),
                'payload': s.get('payload', s.get('title', s.get('text', '')))
            })

    return {
        'reply': result.get('reply', ''),
        'suggestions': normalized_suggestions
    }


def get_fallback_suggestions(context: dict = None) -> List[Dict[str, Any]]:
    """
    Generate fallback suggestions based on context

    Args:
        context: Optional context with conversationId, history, etc.

    Returns:
        list: Default suggestions
    """
    return [
        {
            "title": "Tell me about yourself",
            "action": "fill_input",
            "payload": "How should I structure my 'tell me about yourself' answer?"
        },
        {
            "title": "Behavioral questions",
            "action": "fill_input",
            "payload": "What are the most common behavioral interview questions?"
        },
        {
            "title": "Technical preparation",
            "action": "fill_input",
            "payload": "How can I improve my technical interview skills?"
        }
    ]
