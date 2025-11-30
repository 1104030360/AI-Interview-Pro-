"""
Prompt Templates Module

Standardized prompt templates for AI interactions
"""
from .base import PromptTemplate, JSONPromptTemplate
from .question import QuestionGenerationPrompt
from .coach import CoachChatPrompt

__all__ = [
    'PromptTemplate',
    'JSONPromptTemplate',
    'QuestionGenerationPrompt',
    'CoachChatPrompt'
]
