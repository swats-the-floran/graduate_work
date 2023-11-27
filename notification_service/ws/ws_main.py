import asyncio
import logging

import websockets
from config import Settings
from websockets.exceptions import ConnectionClosedError


logger = logging.getLogger('websockets.server')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())

people: dict = {}


async def message_everybody(message):

    for u in people:
        await people[u].send(message)
        await asyncio.sleep(0.1)


async def welcome(websocket: websockets.WebSocketServerProtocol) -> str:
    name = None
    while not name:
        await websocket.send('Представьтесь!')
        req = await websocket.recv()
        if req.strip() in people:
            await websocket.send(f'Пользователь с ником {req} существует!')
            await asyncio.sleep(1)
        else:
            name = req
    await websocket.send('Чтобы поговорить, напишите "<имя>: <сообщение>". Например: Ира: купи хлеб.')
    await websocket.send('Удалить спамера, напишите "stopspamer: <имя>". Например: stopspamer: Ира')
    await websocket.send('Посмотреть список участников можно командой "?"')
    people[name.strip()] = websocket
    return name


async def receiver(websocket: websockets.WebSocketServerProtocol,) -> None:
    name = await welcome(websocket)
    try:
        while True:
            # Получаем сообщение от абонента и решаем, что с ним делать
            message = (await websocket.recv()).strip()
            # На знак вопроса вернём список ников подключившихся людей
            if message == '?':
                await websocket.send(', '.join(people.keys()))
                continue

            # Eсли пользователь решил удалить спамера- удаляем спамера
            elif message.startswith("stopspamer"):
                spamer = message.split(': ')[1]
                del people[spamer]
                logger.error(f"{spamer} устранен")
                # сообщаем всем пользователям об удалении спамера
                await message_everybody(f"Спамер {spamer} нейтрализован")
            # Остальные сообщения попытаемся проанализировать
            # и отправить нужному собеседнику
            else:
                try:
                    to, text = message.split(': ', 1)
                    if to in people:
                        # Пересылаем сообщение в канал получателя, указав отправителя
                        await people[to].send(f'Сообщение от {name}: {text}')
                    else:
                        await websocket.send(f'Пользователь {to} не найден')
                except ValueError as e:
                    await websocket.send(f'возникла ошибка формата передаваемого сообщения: {e}')
    except ConnectionClosedError:
        _user = name.strip()
        logger.error(f"{_user} вышел")
        del people[_user]

    except KeyError:
        _user = name.strip()
        logger.error(f"{_user} исключен из-за несоблюдения правил чата")
        del people[_user]


# Создаём сервер, который будет обрабатывать подключения
ws_server = websockets.serve(receiver, Settings.WS_HOST, Settings.WS_PORT)

# Запускаем event-loop
loop = asyncio.get_event_loop()
loop.run_until_complete(ws_server)
loop.run_forever()
