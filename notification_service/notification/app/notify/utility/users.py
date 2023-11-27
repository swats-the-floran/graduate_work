class GetUsers:
    def __init__(self, from_age: int = 6, to_age: int = 125, sex: str = 'MF'):
        from_age = from_age
        to_age = to_age
        sex = sex

    def get_users(self):
        """
        Отправляем сигнал в auth сервис
        для получения списка нужных нам пользователей.
        Реализацию метода оставим за рамками данного проекта.
        """
        # client.get_client()
        # data = dict(from_age=self.from_age, to_age=self.to_age, sex=self.sex)
        # response = client.send_post_request('http://auth', data=data)
        context = dict(
            email='Test@test.ru',
            first_name='Tom',
            last_name='Sawyer',
            user_id='123e4567-e89b-12d3-a456-426614174000'
        )
        return [context]
