import psycopg

from config import settings

print(f'🍊 Исходная база данных URL: {settings.db.url}')
print(f'🍊 Целевая база данных URL: {settings.db_profile.url}')

conn = psycopg.connect(settings.db.url)
cur = conn.cursor()

conn_profile = psycopg.connect(settings.db_profile.url)
cur_profile = conn_profile.cursor()

sql_query = "SELECT id, title FROM content.film_work"
cur.execute(sql_query)
films = cur.fetchall()

insert_query = "INSERT INTO content.film (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING"

for film in films:
    cur_profile.execute(insert_query, (str(film[0]), film[1]))

conn_profile.commit()

cur.close()
conn.close()
cur_profile.close()
conn_profile.close()
