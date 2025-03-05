import os
from celery.schedules import timedelta

# Get Redis configuration from environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')

# Broker and result backend URLs
broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Schedule settings
beat_schedule = {
    'fetch-process-values': {
        'task': 'src.subscriber_process.fetch_process_values',
        'schedule': timedelta(seconds=15),
    },
} 