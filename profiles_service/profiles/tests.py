import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Person, Bookmark, Favorite, FilmReview, Film
from profiles.api.v1.serializers import (
    PersonSerializer,
    PersonDetailSerializer,
    BookmarkSerializer,
    FavoriteSerializer,
    FilmReviewSerializer,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_person(db):
    def make_person(**kwargs):
        defaults = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": Person.GenderChoices.MALE,
            "is_active": True
        }
        defaults.update(kwargs)
        return Person.objects.create(**defaults)
    return make_person


@pytest.fixture
def create_film(db):
    def make_film(**kwargs):
        defaults = {
            "name": "Sample Film"
        }
        defaults.update(kwargs)
        return Film.objects.create(**defaults)
    return make_film


@pytest.fixture
def create_bookmark(create_person, create_film, db):
    def make_bookmark(person_id=None, **kwargs):
        person = person_id if person_id else create_person()
        film = create_film()
        defaults = {
            "timecode": 100,
            "comment": "Test Comment",
            "person": person,
            "film": film
        }
        defaults.update(kwargs)
        return Bookmark.objects.create(**defaults)
    return make_bookmark


@pytest.fixture
def create_film_review(create_person, create_film, db):
    def make_film_review(person_id=None, **kwargs):
        person = person_id if person_id else create_person()
        film = create_film()
        defaults = {
            "review_text": "Test review",
            "score": 10,
            "person": person,
            "film": film,
        }
        defaults.update(kwargs)
        return FilmReview.objects.create(**defaults)
    return make_film_review


@pytest.fixture
def create_favorite(create_person, create_film, db):
    def make_favorite(person_id=None, **kwargs):
        person = person_id if person_id else create_person()
        film = create_film()
        defaults = {
            "person": person,
            "film": film,
        }
        defaults.update(kwargs)
        return Favorite.objects(**defaults)
    return make_favorite


@pytest.mark.django_db
def test_person_detail_api(api_client, create_person):
    person = create_person(email="user1@example.com")
    url = reverse('person-detail', args=[person.id])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == PersonSerializer(person).data


@pytest.mark.django_db
def test_bookmarks_api(api_client, create_person, create_bookmark):
    person = create_person()
    bookmarks = [create_bookmark(person_id=person.id) for _ in range(5)]

    url = reverse('person-bookmarks', kwargs={"person_pk": person.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(bookmarks) == len(response.data)


@pytest.mark.django_db
def test_favorites_api(api_client, create_person, create_favorite):
    person = create_person()
    favorites = [create_favorite(person_id=person.id) for _ in range(5)]

    url = reverse('person-favorites', kwargs={"person_pk": person.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(favorites) == len(response.data)


@pytest.mark.django_db
def test_film_review_api(api_client, create_person, create_film_review):
    person = create_person()
    film_reviews = [create_film_review(person_id=person.id) for _ in range(5)]

    url = reverse('person-reviews', kwargs={"person_pk": person.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(film_reviews) == len(response.data)
