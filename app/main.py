from fastapi import FastAPI, BackgroundTasks
from .celery_worker import fetch_geolocation_data

app = FastAPI(title="Geolocation API")

@app.get("/")
async def root():
    return {"message": "Geolocation API is running"}

@app.post("/trigger-geolocation-fetch")
async def trigger_fetch(background_tasks: BackgroundTasks):
    """Manually trigger geolocation data fetch"""
    fetch_geolocation_data.delay()
    return {"message": "Geolocation fetch task has been triggered"} 