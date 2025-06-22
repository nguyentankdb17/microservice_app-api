from fastapi import FastAPI
from src.routes import user
from src.middleware.cors import add_cors
from src.middleware.metrics import (
    metrics_app,
    update_metrics,
)

app = FastAPI()
add_cors(app)

app.mount("/metrics", metrics_app)
app.middleware("http")(update_metrics)

app.include_router(user.router)
