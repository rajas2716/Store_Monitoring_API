# celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('api')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Define the schedule for your hourly task
app.conf.beat_schedule = {
    'my-hourly-task': {
        'task': 'api.tasks.hourly_precomputation',
        'schedule': crontab(minute=0, hour='*'),  # Run every hour at minute 0
    },
}

app.conf.timezone = 'UTC'
