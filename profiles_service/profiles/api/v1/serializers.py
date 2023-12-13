from rest_framework import serializers

from profiles.models import Film, Person, FilmReview, Favorite, Bookmark


class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        read_only_fields = ('id',)
        exclude = ('password',)


class FilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    films = FilmSerializer(many=True, read_only=True)

    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('id', 'person')


class BookmarkSerializer(serializers.ModelSerializer):
    silms = FilmSerializer(many=True, read_only=True)

    class Meta:
        model = Bookmark
        fields = '__all__'
        read_only_fields = ('id', 'person')


class FilmReviewSerializer(serializers.ModelSerializer):
    films = FilmSerializer(many=True, read_only=True)

    class Meta:
        model = FilmReview
        fields = '__all__'
        read_only_fields = ('id', 'person')


