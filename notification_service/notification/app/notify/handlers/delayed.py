from notify.dataclasses import DataModel, UserData
from notify.handlers.base import BaseHandler
from notify.utils import get_rendered_template


class DelayedHandler(BaseHandler):
    template_name = 'films_delayed.html'
    subject = 'Подборка пожеланий к просмотру!'

    def prepare_data(self):
        data = self.nl.notification_data
        receiver = data.get('receiver')
        first_name = receiver.get('first_name')
        films_list = data.get('movies')
        user_list = [UserData(**receiver)]

        values_to_render = dict(first_name=first_name, films_list=films_list)
        template = get_rendered_template(self.template_name, values_to_render)
        subject = self.subject

        data_to_send = dict(user_list=user_list,
                            template=template,
                            subject=subject)

        try:
            return [DataModel(**data_to_send)]
        except Exception as e:
            self.nl.log_error(e)
            self.fail()
