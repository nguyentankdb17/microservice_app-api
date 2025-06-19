from fastapi import FastAPI
from src.routes import user
from src.core.middleware import add_middlewares

app = FastAPI()
add_middlewares(app)
app.include_router(user.router)