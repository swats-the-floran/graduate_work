from enum import Enum


class IndexName(str, Enum):
    MOVIES = "movies"
    PERSONS = "persons"
    GENRES = "genres"


SETTINGS = {
    "refresh_interval": "1s",
    "analysis": {
        "filter": {
            "english_stop": {"type": "stop", "stopwords": "_english_"},
            "english_stemmer": {"type": "stemmer", "language": "english"},
            "english_possessive_stemmer": {"type": "stemmer", "language": "possessive_english"},
            "russian_stop": {"type": "stop", "stopwords": "_russian_"},
            "russian_stemmer": {"type": "stemmer", "language": "russian"},
        },
        "analyzer": {
            "ru_en": {
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "english_stop",
                    "english_stemmer",
                    "english_possessive_stemmer",
                    "russian_stop",
                    "russian_stemmer",
                ],
            },
        },
    },
}

INDEXES = {
    IndexName.MOVIES: {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "keyword"},
            "imdb_rating": {"type": "float"},
            "title": {"type": "text", "analyzer": "ru_en", "fields": {"raw": {"type": "keyword"}}},
            "description": {"type": "text", "analyzer": "ru_en"},
            "genres_name": {"type": "keyword"},
            "directors_name": {"type": "text", "analyzer": "ru_en"},
            "actors_names": {"type": "text", "analyzer": "ru_en"},
            "writers_names": {"type": "text", "analyzer": "ru_en"},
            "genres": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {"id": {"type": "keyword"}, "name": {"type": "text", "analyzer": "ru_en"}},
            },
            "directors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {"id": {"type": "keyword"}, "name": {"type": "text", "analyzer": "ru_en"}},
            },
            "actors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {"id": {"type": "keyword"}, "name": {"type": "text", "analyzer": "ru_en"}},
            },
            "writers": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {"id": {"type": "keyword"}, "name": {"type": "text", "analyzer": "ru_en"}},
            },
        },
    },
    IndexName.GENRES: {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "keyword"},
            "name": {"type": "keyword"},
            "description": {"type": "text", "analyzer": "ru_en"},
        },
    },
    IndexName.PERSONS: {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "keyword"},
            "name": {"type": "text", "analyzer": "ru_en", "fields": {"raw": {"type": "keyword"}}},
        },
    },
}

ES_DATA = {
    IndexName.MOVIES: [
        {
            "id": "b164fef5-0867-46d8-b635-737e1721f6bf",
            "title": "Tar with a Star",
            "description": None,
            "imdb_rating": 6.7,
            "genres": [
                {"id": "0b105f87-e0a5-45dc-8ce7-f8632088f390", "name": "Western"},
                {"id": "6a0a479b-cfec-41ac-b520-41b2b007b611", "name": "Animation"},
                {"id": "a886d0ec-c3f3-4b16-b973-dedcf5bfa395", "name": "Short"},
            ],
            "actors": [
                {"id": "2e01e457-f993-4bfe-87c3-de2ef8626cc7", "name": "Mae Questel"},
                {"id": "448b9382-f235-478b-a013-d127f421ea4a", "name": "Jackson Beck"},
                {"id": "89d4622f-5dde-4257-9401-36e3052de105", "name": "Jack Mercer"},
            ],
            "writers": [
                {"id": "89d4622f-5dde-4257-9401-36e3052de105", "name": "Jack Mercer"},
                {"id": "cb7d11c1-9041-4bf5-84b2-728847bbf035", "name": "Carl Meyer"},
            ],
            "directors": [
                {"id": "3138e609-870f-4764-9a57-97d39feef7a8", "name": "Bill Tytla"},
                {"id": "96f18d84-55e0-4718-b87f-4a9e63544d76", "name": "George Germanetti"},
            ],
        },
        {
            "id": "4df8c0cb-2cbf-4e40-b79c-fb07635775b9",
            "title": "Star Shaped Scar",
            "description": None,
            "imdb_rating": 8,
            "genres": [
                {"id": "6d141ad2-d407-4252-bda4-95590aaf062a", "name": "Documentary"},
                {"id": "a886d0ec-c3f3-4b16-b973-dedcf5bfa395", "name": "Short"},
            ],
            "actors": [{"id": "ae8d0f5e-3ef6-4154-97e7-389995800077", "name": "Jasmin Britney Koskiranta"}],
            "writers": [
                {"id": "2cd4f104-b13d-4ea7-9855-e5657eb177d6", "name": "Virva Kunttu"},
                {"id": "7065d231-afe8-402f-a8ba-7b5f8a29e1fa", "name": "Vuokko Kunttu"},
            ],
            "directors": [
                {"id": "2cd4f104-b13d-4ea7-9855-e5657eb177d6", "name": "Virva Kunttu"},
                {"id": "7065d231-afe8-402f-a8ba-7b5f8a29e1fa", "name": "Vuokko Kunttu"},
            ],
        },
        {
            "id": "a010b701-9a46-4a23-aa5d-b029c18353dd",
            "title": "Big Star's Little Star",
            "description": (
                "British game show presented by Stephen Mulhern in which three celebrity contestants and their "
                "children answer questions about each other to win up to £15,000 for a charity of their choice."
            ),
            "imdb_rating": 6.3,
            "genres": [
                {"id": "5373d043-3f41-4ea8-9947-4b746c601bbd", "name": "Comedy"},
                {"id": "55c723c1-6d90-4a04-a44b-e9792040251a", "name": "Family"},
                {"id": "fb58fd7f-7afd-447f-b833-e51e45e2a778", "name": "Game-Show"},
            ],
            "actors": [{"id": "31b84bca-0603-4b1d-a273-348f0085aa5f", "name": "Stephen Mulhern"}],
            "writers": [],
            "directors": [],
        },
        {
            "id": "ce98c597-42ed-4a60-af20-ec6f985d2ea2",
            "title": "Star",
            "description": (
                "Bradley is a huge movie star who still attends school. "
                "His star status conflicts with his envious teachers and his peers."
            ),
            "imdb_rating": 7,
            "genres": [
                {"id": "5373d043-3f41-4ea8-9947-4b746c601bbd", "name": "Comedy"},
                {"id": "55c723c1-6d90-4a04-a44b-e9792040251a", "name": "Family"},
            ],
            "actors": [
                {"id": "2dfcc75b-24b2-407e-bec8-a3d1d9fdb1fd", "name": "Liam Darbon"},
                {"id": "aa486390-de5d-4988-87f4-cc867539af0b", "name": "Sasha Jackson"},
                {"id": "dbdf8a38-6e59-4c83-bee6-99679cf19ca2", "name": "Tony Graimes"},
                {"id": "fcfe6f65-846f-4fc7-b034-7a9237956b7b", "name": "Matthew Leitch"},
            ],
            "writers": [],
            "directors": [],
        },
        {
            "id": "c516192c-fa26-431f-bb42-4fb6c6075998",
            "title": "To Be a Star",
            "description": None,
            "imdb_rating": 6.1,
            "genres": [
                {"id": "1cacff68-643e-4ddd-8f57-84b62538081a", "name": "Drama"},
                {"id": "5373d043-3f41-4ea8-9947-4b746c601bbd", "name": "Comedy"},
                {"id": "9c91a5b2-eb70-4889-8581-ebe427370edd", "name": "Musical"},
            ],
            "actors": [
                {"id": "578deb06-d70d-4f8c-8174-fe0cec7ae9b7", "name": "Alona Tal"},
                {"id": "5fc24d3d-fa60-4477-ab50-9c1d6abbefee", "name": "Arnon Zadok"},
                {"id": "67503a36-dc38-4104-abfe-3cea92db2e89", "name": "Chaim Elmakias"},
                {"id": "ad4fe264-7624-490e-8c84-6dd53b4c5eab", "name": "Oshri Cohen"},
            ],
            "writers": [{"id": "0d7379fb-3013-4f24-a45b-aa1954c55a8f", "name": "Haim Idisis"}],
            "directors": [{"id": "5fc24d3d-fa60-4477-ab50-9c1d6abbefee", "name": "Arnon Zadok"}],
        },
    ],
    IndexName.GENRES: [
        {"id": "1cacff68-643e-4ddd-8f57-84b62538081a", "name": "Drama"},
        {"id": "5373d043-3f41-4ea8-9947-4b746c601bbd", "name": "Comedy"},
        {"id": "9c91a5b2-eb70-4889-8581-ebe427370edd", "name": "Musical"},
        {"id": "55c723c1-6d90-4a04-a44b-e9792040251a", "name": "Family"},
        {"id": "fb58fd7f-7afd-447f-b833-e51e45e2a778", "name": "Game-Show"},
        {"id": "0b105f87-e0a5-45dc-8ce7-f8632088f390", "name": "Western"},
        {"id": "6a0a479b-cfec-41ac-b520-41b2b007b611", "name": "Animation"},
        {"id": "a886d0ec-c3f3-4b16-b973-dedcf5bfa395", "name": "Short"},
        {"id": "6d141ad2-d407-4252-bda4-95590aaf062a", "name": "Documentary"},
    ],
    IndexName.PERSONS: [
        {"id": "2e01e457-f993-4bfe-87c3-de2ef8626cc7", "name": "Mae Questel"},
        {"id": "448b9382-f235-478b-a013-d127f421ea4a", "name": "Jackson Beck"},
        {"id": "89d4622f-5dde-4257-9401-36e3052de105", "name": "Jack Mercer"},
        {"id": "cb7d11c1-9041-4bf5-84b2-728847bbf035", "name": "Carl Meyer"},
        {"id": "3138e609-870f-4764-9a57-97d39feef7a8", "name": "Bill Tytla"},
        {"id": "96f18d84-55e0-4718-b87f-4a9e63544d76", "name": "George Germanetti"},
        {"id": "ae8d0f5e-3ef6-4154-97e7-389995800077", "name": "Jasmin Britney Koskiranta"},
        {"id": "2cd4f104-b13d-4ea7-9855-e5657eb177d6", "name": "Virva Kunttu"},
        {"id": "7065d231-afe8-402f-a8ba-7b5f8a29e1fa", "name": "Vuokko Kunttu"},
        {"id": "31b84bca-0603-4b1d-a273-348f0085aa5f", "name": "Stephen Mulhern"},
        {"id": "2dfcc75b-24b2-407e-bec8-a3d1d9fdb1fd", "name": "Liam Darbon"},
        {"id": "aa486390-de5d-4988-87f4-cc867539af0b", "name": "Sasha Jackson"},
        {"id": "dbdf8a38-6e59-4c83-bee6-99679cf19ca2", "name": "Tony Graimes"},
        {"id": "fcfe6f65-846f-4fc7-b034-7a9237956b7b", "name": "Matthew Leitch"},
        {"id": "578deb06-d70d-4f8c-8174-fe0cec7ae9b7", "name": "Alona Tal"},
        {"id": "5fc24d3d-fa60-4477-ab50-9c1d6abbefee", "name": "Arnon Zadok"},
        {"id": "67503a36-dc38-4104-abfe-3cea92db2e89", "name": "Chaim Elmakias"},
        {"id": "ad4fe264-7624-490e-8c84-6dd53b4c5eab", "name": "Oshri Cohen"},
        {"id": "0d7379fb-3013-4f24-a45b-aa1954c55a8f", "name": "Haim Idisis"},
    ],
}
