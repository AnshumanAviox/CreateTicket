from celery import Celery
from .geolocation import GeolocationService
from .config import settings

celery = Celery('geolocation_tasks')
celery.config_from_object('celeryconfig')

@celery.task
def fetch_geolocation_data():
    service = GeolocationService()
    
    # Get access token
    access_token = service.get_access_token()
    if not access_token:
        return "Failed to obtain access token"
    
    # Get geo location data
    location_data = service.get_geo_locations(access_token, settings.GROUP_ID)
    if not location_data:
        return "Failed to retrieve geo location data"
    
    # Insert data into database
    try:
        records = location_data.get('results', [])
        if records:
            for record in records:
                service.insert_location_data(record)
            return "All records successfully inserted into database"
        return "No records found to insert"
    except Exception as e:
        return f"Failed to insert some records: {str(e)}" 