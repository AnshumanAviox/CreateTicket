from celery import Celery
from app.geolocation import GeolocationService
from app.config import settings

# Initialize celery app with full import path
celery = Celery('geolocation_tasks', 
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/0')

# Load celery config
celery.config_from_object('celeryconfig')

@celery.task
def fetch_geolocation_data():
    try:
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
    except Exception as e:
        return f"Task failed: {str(e)}"

if __name__ == '__main__':
    celery.start() 