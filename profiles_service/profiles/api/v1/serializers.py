from rest_framework import serializers

from profiles.models import Person, FilmReview, Favorite, Bookmark


class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        read_only_fields = ('id',)
        exclude = ('password',)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('id', 'person')


class BookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark
        fields = '__all__'
        read_only_fields = ('id', 'person')


class FilmReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilmReview
        fields = '__all__'
        read_only_fields = ('id', 'person')


