

class SmsClient:

    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data

    def execute(self):
        # Заглушка для отправки смс
        print('Сообщение отправлено')
