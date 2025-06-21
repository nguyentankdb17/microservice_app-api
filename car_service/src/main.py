from fastapi import FastAPI
from src.routes import car
from src.middleware.cors import add_cors
from src.middleware.metrics import (
    metrics_app,
    update_request_counter,
)

app = FastAPI()

# Middleware for CORS
add_cors(app)

# Middleware for metrics
app.mount("/metrics", metrics_app)
app.middleware("http")(update_request_counter)

# Include the car router
app.include_router(car.router)
