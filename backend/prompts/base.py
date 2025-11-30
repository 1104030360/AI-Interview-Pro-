"""
Base Prompt Template

Abstract base classes for standardized prompt generation
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
import re


class PromptTemplate(ABC):
    """Base prompt template class"""

    template: str = ""
    output_format: str = "text"  # "text" or "json"
    json_schema: Optional[Dict] = None

    def __init__(self, **kwargs):
        self.variables = kwargs

    def render(self) -> str:
        """Render the prompt with variables"""
        rendered = self.template

        # Simple variable substitution
        for key, value in self.variables.items():
            placeholder = "{{" + key + "}}"
            rendered = rendered.replace(placeholder, str(value) if value else "")

        # Add JSON format instruction if needed
        if self.output_format == "json" and self.json_schema:
            rendered += f"\n\nRespond ONLY with valid JSON matching this schema:\n{json.dumps(self.json_schema, indent=2)}"

        return rendered.strip()

    @abstractmethod
    def validate_response(self, response: str) -> Dict[str, Any]:
        """Validate and parse the response"""
        pass


class JSONPromptTemplate(PromptTemplate):
    """Prompt template that expects JSON output"""

    output_format = "json"

    def validate_response(self, response: str) -> Dict[str, Any]:
        """Validate and parse JSON response"""
        # Extract JSON from response
        json_str = self._extract_json(response)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # Try to repair common issues
            data = self._attempt_json_repair(json_str)

        # Schema validation
        if self.json_schema:
            self._validate_schema(data)

        return data

    def _extract_json(self, text: str) -> str:
        """Extract JSON from response text"""
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
            r'```\s*([\s\S]*?)\s*```',       # ``` ... ```
            r'(\{[\s\S]*\})',                # {...}
            r'(\[[\s\S]*\])',                # [...]
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return text.strip()

    def _attempt_json_repair(self, text: str) -> Dict:
        """Attempt to repair common JSON issues"""
        # Remove trailing commas
        text = re.sub(r',\s*([}\]])', r'\1', text)

        # Remove comments
        text = re.sub(r'//[^\n]*', '', text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON response: {text[:200]}...")

    def _validate_schema(self, data: Any) -> None:
        """Simple schema validation"""
        if not self.json_schema:
            return

        if 'required' in self.json_schema:
            if not isinstance(data, dict):
                raise ValueError("Expected object but got non-dict")

            for field in self.json_schema['required']:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

    def get_fallback(self) -> Dict[str, Any]:
        """Return fallback data if parsing fails"""
        return {}
