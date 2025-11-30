"""
Question Generation Prompts

Templates for generating interview questions
"""
from typing import Dict, Any, List
from .base import JSONPromptTemplate


class QuestionGenerationPrompt(JSONPromptTemplate):
    """Interview question generation prompt"""

    template = """You are an expert interview coach. Generate {{count}} interview questions for the following position.

Job Position: {{job_position}}
Experience Level: {{experience_level}}
Focus Areas: {{focus_areas}}

Requirements:
1. Questions should be specific to the job position
2. Include a mix of:
   - Behavioral questions (STAR method applicable)
   - Technical/skill-based questions
   - Situational questions
3. Each question should have:
   - The question text
   - Category (behavioral/technical/situational)
   - Difficulty level (easy/medium/hard)
   - 2-3 key points for a good answer
4. Questions should progressively increase in difficulty

{{additional_context}}"""

    json_schema = {
        "type": "object",
        "required": ["questions"],
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["text", "category", "difficulty"],
                    "properties": {
                        "text": {"type": "string"},
                        "category": {"type": "string"},
                        "difficulty": {"type": "string"},
                        "key_points": {"type": "array"},
                        "follow_up": {"type": "string"}
                    }
                }
            }
        }
    }

    def __init__(
        self,
        job_position: str,
        count: int = 5,
        experience_level: str = "Mid-level",
        focus_areas: str = "General",
        additional_context: str = ""
    ):
        super().__init__(
            job_position=job_position,
            count=count,
            experience_level=experience_level,
            focus_areas=focus_areas,
            additional_context=additional_context
        )

    def get_fallback(self) -> Dict[str, Any]:
        """Return fallback questions if generation fails"""
        return {
            "questions": [
                {
                    "text": "Tell me about yourself and your background.",
                    "category": "behavioral",
                    "difficulty": "easy",
                    "key_points": [
                        "Focus on relevant experience",
                        "Be concise (2-3 minutes)",
                        "End with why you're interested in this role"
                    ]
                },
                {
                    "text": "What are your greatest strengths?",
                    "category": "behavioral",
                    "difficulty": "easy",
                    "key_points": [
                        "Choose strengths relevant to the role",
                        "Provide specific examples",
                        "Show self-awareness"
                    ]
                },
                {
                    "text": "Describe a challenging project you've worked on.",
                    "category": "situational",
                    "difficulty": "medium",
                    "key_points": [
                        "Use STAR method",
                        "Focus on your specific contribution",
                        "Highlight the outcome"
                    ]
                }
            ]
        }


class QuestionRefinementPrompt(JSONPromptTemplate):
    """Prompt for refining or improving a question"""

    template = """As an interview expert, improve this interview question:

Original Question: {{original_question}}
Job Position: {{job_position}}
Desired Difficulty: {{difficulty}}

Please provide:
1. An improved version of the question
2. Why the improvement is better
3. Sample key points for answering"""

    json_schema = {
        "type": "object",
        "required": ["improved_question", "reasoning", "key_points"],
        "properties": {
            "improved_question": {"type": "string"},
            "reasoning": {"type": "string"},
            "key_points": {"type": "array"}
        }
    }

    def __init__(
        self,
        original_question: str,
        job_position: str,
        difficulty: str = "medium"
    ):
        super().__init__(
            original_question=original_question,
            job_position=job_position,
            difficulty=difficulty
        )
