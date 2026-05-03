from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_insight import AIInsight
from app.models.request_log import RequestLog


def generate_insight(db: Session, prompt: str) -> AIInsight:
    total_requests = db.scalar(select(func.count()).select_from(RequestLog)) or 0
    error_count = db.scalar(
        select(func.count()).select_from(RequestLog).where(RequestLog.status_code >= 400)
    ) or 0
    average_latency = db.scalar(select(func.avg(RequestLog.response_time_ms))) or 0
    error_rate = (error_count / total_requests * 100) if total_requests else 0

    summary = (
        f"{prompt} AXIOM analyzed {total_requests} requests. "
        f"The current error rate is {error_rate:.2f}% with {error_count} errors, "
        f"and average latency is {float(average_latency):.2f} ms. "
        "Claude integration is configured as a provider hook; set ANTHROPIC_API_KEY to replace this deterministic local summary with model output."
    )
    insight = AIInsight(prompt=prompt, summary=summary, model=settings.anthropic_model)
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight
