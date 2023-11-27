from notify.dataclasses import DataModel, UserData
from notify.utils import get_rendered_template
from short_links.utils import create_activation_link

from .base import BaseHandler


class WelcomeHandler(BaseHandler):
    template_name = 'welcome_letter.html'
    subject = 'Welcome letter'

    def prepare_data(self):
        data = self.nl.notification_data

        user_list = [UserData(**data)]
        user_id = data.get('user_id')
        activation_link = create_activation_link(user_id)
        values = dict(username=data.get('first_name'), activation_link=activation_link)
        template = get_rendered_template(self.template_name, values)
        subject = self.subject

        data_to_send = dict(user_list=user_list,
                            template=template,
                            subject=subject)

        try:
            return [DataModel(**data_to_send)]
        except Exception as e:
            self.nl.log_error(e)
            self.fail()
