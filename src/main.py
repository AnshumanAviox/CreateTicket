from fastapi import FastAPI
from src.api_endpoints import router

app = FastAPI(title="Process API")

app.include_router(router) 