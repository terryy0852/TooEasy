"""
AI Grading Service
Auto-grades student HTML submissions against a teacher-provided answer key.
"""
import json
import logging
from typing import Dict, Any, Optional

from .base import BaseAIService, AIServiceResult
from .kimi_client import KimiClient

logger = logging.getLogger(__name__)


GRADING_SYSTEM_PROMPT = """You are an expert educational assessment assistant.
Your task is to grade a student's submission by comparing it against the teacher's answer key.

## Rules
1. Evaluate ONLY the student's answers. Ignore HTML markup, CSS, and layout.
2. For each question, assign partial credit where appropriate.
3. Be fair but consistent. Minor spelling errors in non-language subjects may be penalized lightly.
4. For open-ended/essay questions, evaluate based on coverage of key points from the answer key.
5. If the answer key is empty or says "subjective", assign a tentative grade with "subjective": true.

## Output Format (strict JSON)
{
  "overall_grade": "85",
  "overall_feedback": "Concise summary of strengths and 1-2 improvement areas.",
  "questions": [
    {
      "question_id": "q1",
      "student_answer": "summarized or quoted student answer",
      "correct_answer": "from answer key",
      "score": "4/5",
      "is_correct": false,
      "feedback": "Specific feedback for this question."
    }
  ],
  "grading_confidence": "high|medium|low",
  "notes": "Any special observations, e.g., 'Student left Q3 blank'"
}

The "overall_grade" should be a numeric string 0-100 unless the assignment uses letter grades, in which case map numerically first then convert: A=90-100, B=80-89, C=70-79, D=60-69, F=<60.
""".strip()


class AIGradingService(BaseAIService):
    """
    Service: auto-grade a student's HTML submission against an answer key.
    """

    service_name = 'ai_grading'

    def __init__(self, client: Optional[KimiClient] = None):
        self.client = client or KimiClient()

    # ── BaseAIService contract ────────────────────────────────────

    def execute(self, **kwargs) -> AIServiceResult:
        """
        Expected kwargs:
          - answer_key (str): teacher's answer key / expected answers
          - student_html (str): the serialized HTML submission
          - max_score (int|str): optional maximum score (default 100)
          - assignment_title (str): optional context
        """
        answer_key = kwargs.get('answer_key', '')
        student_html = kwargs.get('student_html', '')
        max_score = kwargs.get('max_score', 100)
        assignment_title = kwargs.get('assignment_title', 'Assignment')

        if not answer_key or not answer_key.strip():
            return AIServiceResult(
                success=False,
                error="No answer key provided — cannot auto-grade.",
            )
        if not student_html or not student_html.strip():
            return AIServiceResult(
                success=False,
                error="Empty student submission — cannot grade.",
            )

        messages = self._build_messages(
            answer_key=answer_key,
            student_html=student_html,
            max_score=max_score,
            assignment_title=assignment_title,
        )

        try:
            resp = self.client.chat_completion(
                messages=messages,
                json_mode=True,
                temperature=0.2,
                max_tokens=4096,
            )
            parsed = self.client.extract_json(resp)

            # Normalize grade to string
            grade = str(parsed.get('overall_grade', '')).strip()
            feedback = parsed.get('overall_feedback', '')
            confidence = parsed.get('grading_confidence', 'medium')

            # Build per-question detail for storage
            questions = parsed.get('questions', [])

            usage = resp.get('usage', {})
            tokens = usage.get('total_tokens', 0)

            return AIServiceResult(
                success=True,
                data={
                    'grade': grade,
                    'feedback': feedback,
                    'confidence': confidence,
                    'questions': questions,
                    'notes': parsed.get('notes', ''),
                },
                raw_response=json.dumps(parsed, ensure_ascii=False, indent=2),
                tokens_used=tokens,
            )

        except Exception as e:
            logger.error(f"[AIGradingService] Grading failed: {e}", exc_info=True)
            return AIServiceResult(
                success=False,
                error=str(e),
            )

    def health_check(self) -> bool:
        return self.client.health_check()

    # ── Internals ─────────────────────────────────────────────────

    def _build_messages(
        self,
        answer_key: str,
        student_html: str,
        max_score: Any,
        assignment_title: str,
    ) -> list:
        # Truncate extremely large HTML to avoid token limits
        # Rough heuristic: 1 token ≈ 4 chars for English, 1-2 for CJK
        max_html_chars = 12000
        if len(student_html) > max_html_chars:
            student_html = student_html[:max_html_chars] + "\n...[truncated for length]"

        user_content = f"""Assignment: {assignment_title}
Maximum Score: {max_score}

--- TEACHER ANSWER KEY ---
{answer_key}

--- STUDENT SUBMISSION (HTML) ---
{student_html}

Please grade the submission and return ONLY the JSON object specified in your instructions.
"""
        return [
            {"role": "system", "content": GRADING_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
