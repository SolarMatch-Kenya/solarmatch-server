# celery_config.py
from celery import Celery
import os

redis_url = os.environ.get('REDIS_URL')
if not redis_url:
    raise ValueError("REDIS_URL environment variable is not set.")

# Create the Celery instance here, at the module level
celery = Celery(
    __name__,  # Use a generic name
    broker=redis_url,
    backend=redis_url
)
celery.conf.update(
    broker_connection_retry_on_startup=True
)

def init_celery(app):
    """
    Initializes the Celery instance with the Flask app context.
    """
    celery.conf.update(app.config)
    celery.main = app.import_name  # Link it to the app

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    # We return the app, not celery, just to be conventional
    return app