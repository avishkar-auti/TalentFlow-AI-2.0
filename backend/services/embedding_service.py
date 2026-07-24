"""Gemini-based text embedding service for semantic resume-to-job matching.

Degrades gracefully: if the API key is missing/invalid or the request fails for
any reason, embed_text() returns None and callers fall back to lexical-only
ATS scoring instead of raising — semantic matching is an enhancement, not a
hard dependency for resume processing to succeed.
"""
import asyncio
import logging
import math
import os
from typing import List, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)

_EMBEDDING_MODEL = "models/gemini-embedding-001"
_configured = False


def _ensure_configured() -> bool:
    global _configured
    if _configured:
        return True
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    _configured = True
    return True


async def embed_text(text: str, task_type: str = "SEMANTIC_SIMILARITY") -> Optional[List[float]]:
    """Returns a Gemini embedding vector for the given text, or None if unavailable."""
    text = (text or "").strip()
    if not text:
        return None
    if not _ensure_configured():
        logger.warning("GEMINI_API_KEY not configured — skipping semantic embedding.")
        return None
    try:
        result = await asyncio.to_thread(
            genai.embed_content,
            model=_EMBEDDING_MODEL,
            content=text[:20000],
            task_type=task_type,
        )
        return result.get("embedding")
    except Exception as e:
        logger.warning(f"Gemini embedding request failed, falling back to lexical matching only: {e}")
        return None


def cosine_similarity(a: Optional[List[float]], b: Optional[List[float]]) -> Optional[float]:
    """Returns cosine similarity in [0,1] (negative values clamped to 0), or None if either vector is missing."""
    if not a or not b or len(a) != len(b):
        return None
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return None
    return max(0.0, dot / (norm_a * norm_b))
