import psycopg
from elasticsearch import Elasticsearch
from config import settings

print(f'🍊settings.db.url {settings.db.url}')
print(f'🍊settings.es.url {settings.es.url}')

conn = psycopg.connect(settings.db.url)

cur = conn.cursor()

sql_query = "SELECT id, title FROM content.film_work"


cur.execute(sql_query)
films = cur.fetchall()

cur.close()
conn.close()

es = Elasticsearch(settings.es.url)

index_name = "movies"

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)

for film in films:
    document = {
        "id": str(film[0]),
        "title": film[1]
    }
    es.index(index=index_name, id=document["id"], document=document)
