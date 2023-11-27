from short_links.models import Link


def activate_user_in_auth_service(user_id):
    """
    Отправляем сигнал в auth сервис
    о том что юзера нужно активировать

    Конкретную реализацию оставляем за рамками этой задачи!!!
    """
    # client.get_client()
    # data = dict(user_id=user_id)
    # response = client.send_post_request('http://auth', data=data)

    print('response')


def create_activation_link(user_id):
    short = Link.create_new(user_id)
    return f'http://localhost/short/{short}'
