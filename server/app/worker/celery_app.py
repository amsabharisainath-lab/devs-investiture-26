from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "devs",
    broker=settings.REDIS_URL,
)

celery_app.conf.update(
    task_ignore_result=True,
    task_routes={
        "app.worker.tasks.send_registration_email": {
            "queue": "registration_email",
        },
        "app.worker.tasks.send_od_email": {
            "queue": "od_email",
        },
    },
    task_default_queue="registration_email",
    task_acks_late=True,
    task_track_started=False,
)

celery_app.autodiscover_tasks(["app.worker"])
