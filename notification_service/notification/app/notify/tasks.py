import logging

from celery_once import QueueOnce
from config.celery import TaskQueue, app
from notify.handlers.router import get_handler
from notify.helpers import send_assignment
from notify.models import Assignment, NotificationLog
from notify.utils import unlock_log_finally


logger = logging.getLogger(__name__)


@app.task(base=QueueOnce, queue=TaskQueue.QUEUE_DEFAULT)
@unlock_log_finally
def task_process_log(guid):

    nl = NotificationLog.get_object(guid)

    handler = get_handler(nl)
    handler.process()
    return 'Processed'


@app.task(queue=TaskQueue.QUEUE_DEFAULT)
def task_discover_new(batch_size=50):

    new_guids = list(NotificationLog.new.values_list('guid', flat=True)[:batch_size])

    NotificationLog.objects.filter(guid__in=new_guids).update(locked=True)

    for guid in new_guids:
        task_process_log.apply_async((guid,))
    return len(new_guids)


@app.task(queue=TaskQueue.QUEUE_DEFAULT)
def task_send_assignment(guid: Assignment):
    send_assignment(guid=guid)
