"""
AI Services Configuration
Centralized config for all AI service integrations.
"""
import os

# ── Kimi / Moonshot AI ───────────────────────────────────────────
KIMI_API_KEY = os.environ.get('KIMI_API_KEY', '')
KIMI_API_BASE = os.environ.get('KIMI_API_BASE', 'https://api.moonshot.cn/v1')
KIMI_MODEL = os.environ.get('KIMI_MODEL', 'kimi-latest')

# ── Grading defaults ─────────────────────────────────────────────
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.2   # low temp for consistent grading

# ── Feature flags ────────────────────────────────────────────────
AI_GRADING_ENABLED = os.environ.get('AI_GRADING_ENABLED', 'true').lower() in ('1', 'true', 'yes')

# ── Rate limiting ────────────────────────────────────────────────
MAX_CONCURRENT_AI_CALLS = int(os.environ.get('MAX_CONCURRENT_AI_CALLS', '3'))
AI_REQUEST_TIMEOUT = int(os.environ.get('AI_REQUEST_TIMEOUT', '60'))
