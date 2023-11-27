from __future__ import annotations

import abc


class Transformer(abc.ABC):
    @abc.abstractmethod
    def transform(self, batch: list[dict]) -> list[dict]:
        """return transformed data"""


class MovieTransformer(Transformer):
    """Преобразуем данные Postgresql под формат ElasticSearch"""

    def transform(self, batch: list[dict]) -> list[dict]:
        transformed = []
        for row in batch:
            transformed_row = dict(
                id=row["id"],
                imdb_rating=row["imdb_rating"],
                title=row["title"],
                description=row["description"],
                genres_name=row["genres_name"] if row["genres_name"] is not None else [],
                directors_name=row["directors_names"] if row["directors_names"] is not None else [],
                actors_names=row["actors_names"] if row["actors_names"] is not None else [],
                writers_names=row["writers_names"] if row["writers_names"] is not None else [],
                genres=row["genres"] if row["genres"] is not None else [],
                directors=row["directors"] if row["directors"] is not None else [],
                actors=row["actors"] if row["actors"] is not None else [],
                writers=row["writers"] if row["writers"] is not None else [],
            )
            transformed.append(transformed_row)
        return transformed


class GenreTransformer(Transformer):
    def transform(self, batch: list[dict]) -> list[dict]:
        transformed = []
        for row in batch:
            transformed_row = dict(id=row["id"], name=row["name"], description=row["description"])
            transformed.append(transformed_row)
        return transformed


class PersonTransformer(Transformer):
    def transform(self, batch: list[dict]) -> list[dict]:
        transformed = []
        for row in batch:
            transformed_row = dict(id=row["id"], name=row["full_name"])
            transformed.append(transformed_row)
        return transformed
