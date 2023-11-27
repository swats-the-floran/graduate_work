from typing import Optional

from aiokafka import AIOKafkaProducer

from db.broker import BrokerInterface

# переменная хранит объект подключения после чего передачи
producer: Optional[AIOKafkaProducer] = None


async def get_broker_producer() -> Optional[AIOKafkaProducer]:
    return producer


class KafkaMixin(BrokerInterface):

    def __init__(self, producer: AIOKafkaProducer):
        self.producer: AIOKafkaProducer = producer

    async def set_data(self, topic: str, key: bytes, value: bytes) -> None:
        await self.producer.send(topic=topic, key=key, value=value)

