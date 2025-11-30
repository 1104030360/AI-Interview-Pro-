"""
AI Coach Prompts

Templates for AI coaching conversations
"""
from typing import Dict, Any, List, Optional
from .base import JSONPromptTemplate


class CoachChatPrompt(JSONPromptTemplate):
    """AI Coach chat conversation prompt"""

    template = """{{global_prompt}}

{{coach_prompt}}

You are an AI interview coach helping users prepare for job interviews.

Guidelines:
1. Be supportive and encouraging while providing constructive feedback
2. Offer specific, actionable advice
3. Use the STAR method when discussing behavioral questions
4. Tailor advice to the user's experience level and target role
5. Always end with 2-3 follow-up suggestions

{{context}}

User Message: {{message}}"""

    json_schema = {
        "type": "object",
        "required": ["reply"],
        "properties": {
            "reply": {"type": "string"},
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 5
            },
            "resources": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "type": {"type": "string"}
                    }
                }
            }
        }
    }

    def __init__(
        self,
        message: str,
        global_prompt: str = "",
        coach_prompt: str = "",
        context: str = ""
    ):
        super().__init__(
            message=message,
            global_prompt=global_prompt,
            coach_prompt=coach_prompt,
            context=context
        )

    def get_fallback(self) -> Dict[str, Any]:
        """Return fallback response if generation fails"""
        return {
            "reply": "I apologize, but I'm having trouble processing your request right now. Please try asking your question again, or rephrase it.",
            "suggestions": [
                "How should I prepare for a technical interview?",
                "What are common behavioral interview questions?",
                "How can I improve my interview skills?"
            ]
        }


class FeedbackPrompt(JSONPromptTemplate):
    """Prompt for generating feedback on interview performance"""

    template = """Analyze this interview response and provide constructive feedback.

Question: {{question}}
User's Answer: {{answer}}
Job Position: {{job_position}}
Question Type: {{question_type}}

Evaluate based on:
1. Relevance to the question
2. Structure and clarity
3. Use of specific examples
4. Technical accuracy (if applicable)
5. Overall effectiveness

Provide:
- A score out of 100
- 2-3 strengths
- 2-3 areas for improvement
- Specific suggestions for improvement"""

    json_schema = {
        "type": "object",
        "required": ["score", "strengths", "improvements", "suggestions"],
        "properties": {
            "score": {"type": "number"},
            "strengths": {"type": "array"},
            "improvements": {"type": "array"},
            "suggestions": {"type": "array"}
        }
    }

    def __init__(
        self,
        question: str,
        answer: str,
        job_position: str = "General",
        question_type: str = "behavioral"
    ):
        super().__init__(
            question=question,
            answer=answer,
            job_position=job_position,
            question_type=question_type
        )

    def get_fallback(self) -> Dict[str, Any]:
        return {
            "score": 70,
            "strengths": ["Attempted to answer the question"],
            "improvements": ["Could provide more specific examples"],
            "suggestions": ["Try using the STAR method for behavioral questions"]
        }
