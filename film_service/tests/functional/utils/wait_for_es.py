import time

from elasticsearch import Elasticsearch

from tests.functional.settings import settings

if __name__ == "__main__":
    with Elasticsearch(hosts=settings.elastic_dsn) as es_client:
        while True:
            if es_client.ping():
                print("ES start...")
                break
            time.sleep(1)
