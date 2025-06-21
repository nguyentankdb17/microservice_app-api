from prometheus_client import Counter, make_asgi_app
import re
from starlette.responses import Response

# Prometheus ASGI app
metrics_app = make_asgi_app()

# Prometheus metrics definitions
REQUEST_COUNTER = Counter(
    "api_requests_total",
    "Total number of requests to the api",
    ["method", "handler", "status_code"],
)


# Middleware to update metrics on each request
async def update_request_counter(request, call_next):
    route_path = request.url.path
    method = request.method

    # Simplify the route path by removing dynamic segments
    # e.g., /cars/update/1 -> /cars/update
    handler_path = re.sub(r"/\d+($|/)", "/", route_path).rstrip("/")
    if not handler_path:
        handler_path = "/"

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        status_code = 500
        response = Response("Internal Server Error", status_code=status_code)
    finally:
        REQUEST_COUNTER.labels(
            method=method, handler=handler_path, status_code=status_code
        ).inc()

    return response
