from prometheus_client import Counter, Gauge, make_asgi_app
import psutil
import re

# Prometheus ASGI app
metrics_app = make_asgi_app()

# Prometheus metrics definitions
REQUEST_COUNTER = Counter(
    "api_requests_total",
    "Total number of requests to the api",
    ["endpoint"],
)

CPU_USAGE_GAUGE = Gauge(
    "system_cpu_usage_percent",
    "System CPU usage in percent",
)

MEMORY_USAGE_GAUGE = Gauge(
    "system_memory_usage_percent",
    "System memory usage in percent",
)

# Middleware to update metrics on each request
async def update_request_counter(request, call_next):
    route_path = request.url.path

    # Simplify the route path by removing dynamic segments
    # e.g., /cars/update/1 -> /cars/update
    simplified_endpoint = re.sub(r"/\d+($|/)", "/", route_path).rstrip("/")
    if not simplified_endpoint:
        simplified_endpoint = "/"

    REQUEST_COUNTER.labels(endpoint=simplified_endpoint).inc()

    response = await call_next(request)
    return response


# Middleware to update system resource metrics    
async def update_system_metrics(request, call_next):
    CPU_USAGE_GAUGE.set(psutil.cpu_percent())
    MEMORY_USAGE_GAUGE.set(psutil.virtual_memory().percent)

    response = await call_next(request)
    return response
