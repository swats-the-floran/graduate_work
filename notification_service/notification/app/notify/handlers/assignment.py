from notify.dataclasses import DataModel, UserData
from notify.handlers.base import BaseHandler
from notify.utils import get_rendered_template


class NewAssignmentHandler(BaseHandler):
    template_name = 'assignment.html'

    def prepare_data(self):
        data = self.nl.notification_data

        receivers = data.get('receivers', [])
        subject = data.get('subject')
        title = data.get('title')
        message = data.get('message')

        user_list = [UserData(**data) for data in receivers]

        prepared_data = list()
        for receiver in user_list:
            first_name = receiver.first_name

            values_to_render = dict(first_name=first_name, title=title, message=message)
            template = get_rendered_template(self.template_name, values_to_render)

            data_to_send = dict(user_list=[receiver],
                                template=template,
                                subject=subject)
            try:
                prepared_data.append(DataModel(**data_to_send))
            except Exception as e:
                self.nl.log_error(e)
                self.fail()
            return prepared_data
