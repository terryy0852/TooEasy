"""
AI Services Package
All AI-powered features live here for clean separation from the Flask app.
"""
from .base import BaseAIService, AIServiceResult
from .kimi_client import KimiClient
from .grading_service import AIGradingService

__all__ = [
    'BaseAIService',
    'AIServiceResult',
    'KimiClient',
    'AIGradingService',
]
