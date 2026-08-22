import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Prometheus Metrics Definitions
HTTP_REQUESTS_TOTAL = Counter(
    "globetrotter_http_requests_total",
    "Total count of HTTP requests processed",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "globetrotter_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

ACTIVE_WEBSOCKETS = Gauge(
    "globetrotter_active_websockets",
    "Number of active WebSocket client connections",
    ["channel"],
)

ML_INFERENCE_DURATION_SECONDS = Histogram(
    "globetrotter_ml_inference_duration_seconds",
    "Latency of ML model inferences",
    ["model_name"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

AUDIT_EVENTS_TOTAL = Counter(
    "globetrotter_audit_events_total",
    "Total count of audit log events recorded",
    ["action"],
)


def track_ml_inference(model_name: str):
    """Context manager or helper to measure ML inference latency."""
    class InferenceTracker:
        def __enter__(self):
            self.start = time.time()
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start
            ML_INFERENCE_DURATION_SECONDS.labels(model_name=model_name).observe(duration)
    return InferenceTracker()


def get_metrics_payload() -> tuple[bytes, str]:
    """Generates the latest Prometheus metrics in text format."""
    return generate_latest(), CONTENT_TYPE_LATEST
