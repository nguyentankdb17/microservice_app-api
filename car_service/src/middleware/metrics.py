import time
from prometheus_client import Counter, make_asgi_app
from prometheus_client import Summary
import re
from starlette.responses import Response

# Prometheus ASGI app
metrics_app = make_asgi_app()

# Summary for request duration in milliseconds
REQUEST_TIME_MS = Summary(
    "api_request_duration",
    "Request duration in milliseconds",
    ["method", "handler"],
)

# Counter for total requests
REQUEST_COUNTER = Counter(
    "api_requests_total",
    "Total number of requests to the api",
    ["method", "handler", "status_code"],
)

# Counter for errors (4xx/5xx)
ERROR_COUNTER = Counter(
    "api_error_total",
    "Total number of 4xx/5xx errors",
    ["method", "handler", "status_code"],
)


# Middleware to update metrics on each request
async def update_metrics(request, call_next):
    route_path = request.url.path
    method = request.method

    # Simplify the route path by removing dynamic segments
    # e.g., /cars/update/1 -> /cars/update
    handler_path = re.sub(r"/\d+($|/)", "/", route_path).rstrip("/")
    if not handler_path:
        handler_path = "/"

    # Start the timer for request duration
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        status_code = 500
        response = Response("Internal Server Error", status_code=status_code)
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000
        REQUEST_TIME_MS.labels(method=method, handler=handler_path).observe(
            duration_ms
        )

        REQUEST_COUNTER.labels(
            method=method, handler=handler_path, status_code=status_code
        ).inc()

        if status_code >= 400:
            ERROR_COUNTER.labels(
                method=method, handler=handler_path, status_code=status_code
            ).inc()

    return response
