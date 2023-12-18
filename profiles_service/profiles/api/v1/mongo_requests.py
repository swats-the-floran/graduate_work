import logging
from typing import OrderedDict

import requests
from profiles.config import settings


class MongodbMixin:
    @staticmethod
    def _get_reviews_likes(reviews_data: OrderedDict) -> OrderedDict:

        params = ''
        for review in reviews_data:
            params += f'review_ids={review["id"]}&'
        url = settings.url + params

        try:
            resp = requests.get(url, timeout=2)
            review_scores = resp.json()
        except Exception as e:
            logging.error(e)
            return reviews_data

        if not resp.ok:
            return reviews_data

        for review_score in review_scores:
            review_data = next(filter(lambda review: review['id'] == review_score['review_id'],
                                      reviews_data))  # find review for which we got likes
            review_data.update({'score': review_score['score']})
            review_data.update({'quantity': review_score['quantity']})

        return reviews_data

    @staticmethod
    def _get_films_likes(films_data: OrderedDict) -> OrderedDict:
        params = ''
        for film in films_data:
            params += f'film_ids={film["film"]["id"]}&'
        url = settings.ugc.url_film_ratings + params

        try:
            resp = requests.get(url, timeout=2)
            film_scores = resp.json()
        except Exception as e:
            logging.error(e)
            return films_data

        if not resp.ok:
            return films_data

        for film_score in film_scores:
            film_data = next(filter(lambda film: film['film']['id'] == film_score['movie_id'], films_data))
            film_data['film'].update({'score': film_score['score']})
            film_data['film'].update({'quantity': film_score['quantity']})

        return films_data


