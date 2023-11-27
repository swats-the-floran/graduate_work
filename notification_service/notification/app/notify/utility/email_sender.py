import logging
from itertools import chain, islice

from config import settings
from notify import DataModel
from notify.utility.sms_sender import SmsClient
from python_http_client.exceptions import HTTPError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To


class SendgridSender:
    def __init__(self, data: DataModel):
        self._data = data

    @property
    def data(self):
        return self._data

    def _send(self, batch_address: list):
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=batch_address,
            subject=self.data.subject,
            html_content=self.data.template,
            is_multiple=True)
        logging.error(batch_address)

        try:
            sg = SendGridAPIClient(settings.SENDGRID_API)
            response = sg.send(message)
            print(response)
            logging.error(response)

        except HTTPError as e:
            logging.exception('Error sending email')
            raise e
        else:
            if response.status_code != 202:
                logging.error(f'Error send email, {response}')

    def _batcher(self):
        to_emails = (To(email=u.email,  # update with your email
                        name=f'{u.first_name}'
                        ) for u in self.data.user_list)

        # {
        #     '{{name}}': 'Joe',
        #     '{{link}}': 'https://github.com/',
        #     '{{event}}': 'Developers Anonymous'
        # }

        def chunks(iterable, size=1):
            iterator = iter(iterable)
            for first in iterator:
                yield chain([first], islice(iterator, size - 1))

        return chunks(to_emails, settings.BATCH_SIZE)

    def execute(self):
        for batch in self._batcher():
            b = list(batch)
            self._send(batch_address=b)
            logging.info(f'Handled {len(b)} notifications')


def get_notification_client(data, transport):
    if transport == 'email':
        return SendgridSender(data)
    elif transport == 'sms':
        return SmsClient(data)
