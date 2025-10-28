# src/celery_config.py
from celery import Celery
import os

def make_celery(app):
    """
    Configures Celery with the Flask app context.
    """
    redis_url = os.environ.get('REDIS_URL')
    if not redis_url:
        raise ValueError("REDIS_URL environment variable is not set.")

    celery = Celery(
        app.import_name,
        broker=redis_url,
        backend=redis_url  # Use Redis as the result backend too
    )
    celery.conf.update(
        broker_connection_retry_on_startup=True
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery