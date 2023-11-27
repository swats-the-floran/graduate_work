from random import randint
from time import sleep

from kafka import KafkaProducer


MOVIE_LENGTH = 60
MOVIES_QUANTITY = 200
USER_QUANTITTY = 1000


producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

for i in range(10000):
    producer.send(
        topic='views',
        value=bytes(str(randint(1, MOVIE_LENGTH)), 'utf-8'),
        key=bytes(str(randint(1, USER_QUANTITTY)) + '_' + str(randint(1, MOVIES_QUANTITY)), 'utf-8'),
    )

sleep(10)
