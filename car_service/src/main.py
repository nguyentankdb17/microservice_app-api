from fastapi import FastAPI
from src.routes import car
from src.middleware.cors import add_cors
from src.middleware.metrics import metrics_app, update_request_counter, update_system_metrics

app = FastAPI()
add_cors(app)

app.mount("/metrics", metrics_app)
app.middleware("http")(update_request_counter)
app.middleware("http")(update_system_metrics)

app.include_router(car.router)
