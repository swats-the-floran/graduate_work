import multiprocessing as mp
from time import sleep

from clickhouse_driver import Client
from kafka import KafkaConsumer


clickhouse_client = Client(host='clickhouse-node1')
CLICKHOUSE_DB_NAME = 'movies'
CLICKHOUSE_TABLE_NAME = 'views'

def get_query(messages) -> str:
    if not messages:
        return ''

    query_string = f'INSERT INTO {CLICKHOUSE_DB_NAME}.{CLICKHOUSE_TABLE_NAME} (user_id, movie_id, chunk) VALUES '
    for message in messages:
        key = message.key.decode().split('_')

        query_string += f' ({int(key[0])}, {int(key[1])}, {int(message.value)}), '

    return query_string[:-2]


def load_messages():
    kafka_consumer = KafkaConsumer(
        'views',
        bootstrap_servers=['broker:29092'],
        auto_offset_reset='earliest',
        group_id='echo-messages-to-stdout',
        enable_auto_commit=False,
    )

    messages = []

    while True:
        batch = kafka_consumer.poll(max_records=10000)
        values = batch.values()
        for consumer_record in values:
            for message in consumer_record:
                messages.append(message)
                if len(messages) == 10000:
                    query_string = get_query(messages)
                    if not query_string:
                        continue
                    clickhouse_client.execute(query_string)
                    messages = []
                    kafka_consumer.commit()
        sleep(30)


def create_clickhouse_table():
    clickhouse_client.execute(f'CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB_NAME} ON CLUSTER company_cluster')
    clickhouse_client.execute(f'''
        CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.{CLICKHOUSE_TABLE_NAME} ON CLUSTER company_cluster (
            user_id int,
            movie_id int,
            chunk int
        )
        Engine=MergeTree()
        ORDER BY (user_id)
    ''')


if __name__ == '__main__':
    # create_clickhouse_table()
    load_messages()


    # p1 = mp.Process(target=load_messages)
    # p2 = mp.Process(target=load_messages)
    # p3 = mp.Process(target=load_messages)
    #
    # p1.start()
    # p2.start()
    # p3.start()
