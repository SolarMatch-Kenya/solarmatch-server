# run_tasks.py
import sys
from celery_config import celery
from kombu.simple import SimpleQueue

# This is the name of your Celery queue
# The default is 'celery'
QUEUE_NAME = 'celery'

def get_pending_task_count():
    """Checks Redis for pending tasks without needing a full worker."""
    try:
        with celery.broker_connection() as conn:
            simple_queue = SimpleQueue(conn, QUEUE_NAME)
            return simple_queue.qsize()
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        return 0

if __name__ == "__main__":
    count = get_pending_task_count()
    
    if count == 0:
        print("No pending tasks. Exiting.")
        sys.exit(0)
        
    print(f"Found {count} pending tasks. Starting worker to process them.")
    
    # This is the magic command.
    # It starts a worker, processes all available tasks,
    # and then EXITS when the queue is empty.
    # This is exactly what a cron job needs.
    celery.worker_main(
        argv=[
            'worker',
            '--loglevel=info',
            '--concurrency=1',  # Keep it light for the free tier
            '--pool=solo',      # Use a simple single-threaded pool
            '--autoscale=1,1',  # Only run one task at a time
            '--quiet',
            '--perform-subprocess-exec', # Ensures it exits cleanly
            '--use-logcolor=False'
        ]
    )