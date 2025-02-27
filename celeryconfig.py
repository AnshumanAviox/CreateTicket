# Broker settings
broker_url = 'redis://35.88.94.48:6379/0'
result_backend = 'redis://35.88.94.48:6379/0'

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Schedule settings
beat_schedule = {
    'collect-gps-data-every-5-minutes': {
        'task': 'tasks.collect_gps_data',
        'schedule': 300.0,  # 5 minutes in seconds
    },
} 