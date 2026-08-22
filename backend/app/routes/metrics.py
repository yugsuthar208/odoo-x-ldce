from fastapi import APIRouter, Response
from app.services.metrics import get_metrics_payload

router = APIRouter(tags=["Observability & Metrics"])


@router.get("/metrics", summary="Prometheus Metrics Endpoint", description="Returns Prometheus-formatted metrics.")
async def metrics_endpoint():
    """Exposes real-time system metrics for Prometheus scraping."""
    data, content_type = get_metrics_payload()
    return Response(content=data, media_type=content_type)
