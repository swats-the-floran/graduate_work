from notify.models import NotificationLog


def create_notification_log(nl_type, data):
    return NotificationLog.create_by_type(nl_type, data)
