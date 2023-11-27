from notify.dataclasses import DataModel, UserData
from notify.utils import get_rendered_template

from .base import BaseHandler


class BirthdayHandler(BaseHandler):
    template_name = 'happy_birthday.html'
    subject = 'Congratulations!!!'

    def __init__(self, nl):
        super().__init__(nl)

    def prepare_data(self):
        data = self.nl.notification_data

        receivers = data.get('receivers')

        user_list = [UserData(**data) for data in receivers]

        prepared_data = list()
        for receiver in user_list:
            first_name = receiver.first_name

            values_to_render = dict(first_name=first_name, message=data.get('message', ''))
            template = get_rendered_template(self.template_name, values_to_render)

            data_to_send = dict(user_list=[receiver],
                                template=template,
                                subject=self.subject)
            try:
                prepared_data.append(DataModel(**data_to_send))
            except Exception as e:
                self.nl.log_error(e)
                self.fail()

            return prepared_data
