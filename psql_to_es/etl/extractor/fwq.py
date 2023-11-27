film_work_query: str = """
SELECT
    fw.id,
    fw.title,
    fw.description,
    fw.rating as imdb_rating,
    fw.created,
    fw.modified,
    ARRAY_AGG(DISTINCT g.name) as genres_name,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor') as actors_names,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer') as writers_names,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director') as directors_names,
    COALESCE (JSON_AGG(DISTINCT jsonb_build_object('id', g.id, 'name', g.name))) as genres,
    COALESCE (JSON_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
        FILTER (WHERE pfw.role = 'director' and p.id IS NOT NULL), '[]'
    ) as directors,
    COALESCE (JSON_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
        FILTER (WHERE pfw.role = 'actor' and p.id IS NOT NULL), '[]'
    ) as actors,
    COALESCE (JSON_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
        FILTER (WHERE pfw.role = 'writer' and p.id IS NOT NULL), '[]'
    ) as writers
FROM
    content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE
    fw.modified > %s OR p.modified > %s OR g.modified > %s
GROUP BY fw.id
ORDER BY fw.modified DESC
"""

genre_query: str = """
SELECT
    g.id,
    g.name,
    g.description,
    g.modified
FROM
    content.genre g
WHERE
    g.modified > %s
GROUP BY g.id
ORDER BY g.modified DESC
"""

person_query: str = """
SELECT
    p.id,
    p.full_name,
    p.modified
FROM
    content.person p
WHERE
    p.modified > %s
GROUP BY p.id
ORDER BY p.modified DESC
"""
