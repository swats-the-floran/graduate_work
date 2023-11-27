from notify.dataclasses import DataModel, UserData
from notify.handlers.base import BaseHandler
from notify.utils import get_rendered_template


class NewMovieHandler(BaseHandler):
    template_name = 'new_movie.html'
    subject = 'В сервисе Yandex films вышел новый фильм!'

    def prepare_data(self):
        data = self.nl.notification_data

        receivers = data.get('receivers', [])
        movie_name = data.get('movie_name')
        movie_link = data.get('movie_link')
        movie_description = data.get('movie_description')
        subject = self.subject

        user_list = [UserData(**data) for data in receivers]

        prepared_data = list()
        for receiver in user_list:
            first_name = receiver.first_name

            values_to_render = dict(first_name=first_name, movie_name=movie_name, movie_link=movie_link,
                                    movie_description=movie_description)
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
