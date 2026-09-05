from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "budget_tracker",
    broker=settings.rabbitmq_url,
    backend=None,
)
celery_app.conf.update(
    task_default_queue=settings.transaction_queue_name,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=settings.broker_connection_retry_on_startup,
)
celery_app.autodiscover_tasks(["app.worker.tasks"])
