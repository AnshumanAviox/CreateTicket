broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

beat_schedule = {
    'fetch-geolocation-every-5-minutes': {
        'task': 'app.celery_worker.fetch_geolocation_data',
        'schedule': 300.0,  # 5 minutes in seconds
    },
} 