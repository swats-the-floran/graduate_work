from notify.models import Assignment, NotificationTypes
from notify.utility.users import GetUsers
from restapi.utils import create_notification_log


def send_assignment(guid):
    log_type = NotificationTypes.assignment
    assignment = Assignment.get_object(guid)

    receivers = GetUsers(
        from_age=assignment.from_age,
        to_age=assignment.to_age,
        sex=assignment.sex
    ).get_users()

    if not receivers:
        assignment.error = 'Отсутствуют пользователи в заданном критерии.'
        assignment.save(update_fields=['error'])
        return

    data = dict(
        receivers=receivers,
        subject=assignment.subject,
        title=assignment.title,
        message=assignment.message
    )
    create_notification_log(log_type, data)
    assignment.sent = True
    assignment.save(update_fields=['sent'])
