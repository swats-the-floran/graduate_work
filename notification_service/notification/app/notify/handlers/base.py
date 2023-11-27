from django.utils import timezone
from notify.models import NotificationLog, NotificationStages
from notify.utility.email_sender import get_notification_client


MAX_SEND_RETRIES = 5


class BaseHandler:

    def __init__(self, nl: NotificationLog):
        self.nl = nl

    def process(self):

        if self.nl.stage == NotificationStages.new:
            self.send()

        if self.nl.stage == NotificationStages.failed:
            if self.nl.send_tries < MAX_SEND_RETRIES:
                self.send()
        # unlock
        self.nl.unlock()

    def send(self):
        transport = self.nl.transport
        data_to_send = self.prepare_data()

        for data in data_to_send:

            notification_client = get_notification_client(data, transport)

            try:
                notification_client.execute()
            except Exception as e:
                self.nl.log_error(e)
                self.nl.change_stage(NotificationStages.failed)
            else:
                message = f'Success at {timezone.now()}'
                self.nl.log_success(message)
                self.nl.change_stage(NotificationStages.success, save=False)

            self.nl.send_tries += 1
            self.nl.save()

    def prepare_data(self):
        raise Exception('Not implemented')

    def fail(self):
        self.nl.change_stage(NotificationStages.failed)
