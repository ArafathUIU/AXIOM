import json
import logging
from urllib.error import URLError
from urllib.request import Request, urlopen

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_insight import AIInsight
from app.models.request_log import RequestLog

logger = logging.getLogger(__name__)


def generate_insight(db: Session, prompt: str) -> AIInsight:
    total_requests = db.scalar(select(func.count()).select_from(RequestLog)) or 0
    error_count = db.scalar(
        select(func.count()).select_from(RequestLog).where(RequestLog.status_code >= 400)
    ) or 0
    average_latency = db.scalar(select(func.avg(RequestLog.response_time_ms))) or 0
    error_rate = (error_count / total_requests * 100) if total_requests else 0

    context = (
        f"AXIOM analyzed {total_requests} requests. "
        f"The current error rate is {error_rate:.2f}% with {error_count} errors, "
        f"and average latency is {float(average_latency):.2f} ms."
    )
    summary = _generate_gemini_summary(prompt, context) or _local_summary(prompt, context)
    insight = AIInsight(prompt=prompt, summary=summary, model=settings.gemini_model)
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


def _local_summary(prompt: str, context: str) -> str:
    return (
        f"{prompt} {context} "
        "Set GEMINI_API_KEY to generate model-backed operational insights."
    )


def _generate_gemini_summary(prompt: str, context: str) -> str | None:
    if not settings.gemini_api_key:
        return None

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "You are AXIOM, an API observability assistant. "
                            "Explain the API health clearly and concisely.\n\n"
                            f"Operator question: {prompt}\n"
                            f"Current metrics: {context}"
                        )
                    }
                ]
            }
        ]
    }
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("Gemini insight generation failed: %s", exc)
        return None

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        logger.warning("Gemini returned an unexpected response: %s", exc)
        return None
