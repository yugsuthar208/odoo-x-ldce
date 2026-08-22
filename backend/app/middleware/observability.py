import time
import uuid
import json
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure Structured JSON Formatter
class JSONFormatter(logging.Formatter):
    """Custom logging formatter outputting structured JSON logs."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "correlation_id"):
            log_obj["correlation_id"] = record.correlation_id
        if hasattr(record, "path"):
            log_obj["path"] = record.path
        if hasattr(record, "method"):
            log_obj["method"] = record.method
        if hasattr(record, "status_code"):
            log_obj["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


# Initialize Application Logger
logger = logging.getLogger("globetrotter.observability")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.handlers = [handler]
logger.setLevel(logging.INFO)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Extracts or assigns an X-Correlation-ID header.
    2. Logs structured request/response metadata.
    3. Measures and logs request execution latency.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        start_time = time.time()
        response: Response = None

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Attach correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            # Log structured access event (skipping metrics endpoint to reduce noise)
            if not request.url.path.endswith("/metrics"):
                extra = {
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
                logger.info(
                    f"{request.method} {request.url.path} completed with {response.status_code} in {duration_ms}ms",
                    extra=extra
                )
            return response
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            extra = {
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
            }
            logger.error(
                f"Unhandled error processing {request.method} {request.url.path}: {str(exc)}",
                exc_info=True,
                extra=extra
            )
            raise exc
