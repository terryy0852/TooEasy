"""
Base AI Service
Abstract base class that all AI-powered features must implement.
This ensures a consistent interface for future extensions (tutoring,
assignment generation, analytics, etc.).
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AIServiceResult:
    """Standardized result wrapper for all AI service calls."""

    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        raw_response: Optional[str] = None,
        tokens_used: int = 0,
    ):
        self.success = success
        self.data = data or {}
        self.error = error
        self.raw_response = raw_response
        self.tokens_used = tokens_used

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'tokens_used': self.tokens_used,
        }


class BaseAIService(ABC):
    """
    Abstract base for every AI feature.

    Subclasses must implement:
      - service_name: str identifier
      - execute(**kwargs) -> AIServiceResult
    """

    service_name: str = 'base'

    @abstractmethod
    def execute(self, **kwargs) -> AIServiceResult:
        """Run the AI-powered operation."""
        pass

    def health_check(self) -> bool:
        """Override to verify external API connectivity."""
        return True
