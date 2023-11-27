import time

from redis import Redis

from tests.functional.settings import settings

if __name__ == "__main__":
    with Redis(host=settings.redis_host, port=settings.redis_port) as redis:
        while True:
            if redis.ping():
                print("Redis start...")
                break
            time.sleep(1)
