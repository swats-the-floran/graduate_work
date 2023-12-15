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


class FilmScoreSerializer(FilmSerializer):
    score = serializers.IntegerField()
    likes = serializers.IntegerField()


class FavoriteSerializer(serializers.ModelSerializer):
    film = FilmSerializer(many=False, read_only=True)

    class Meta:
        model = Favorite
        exclude = ('created', 'modified')
        read_only_fields = ('id', 'person')


class BookmarkSerializer(serializers.ModelSerializer):
    film = FilmSerializer(many=False, read_only=True)

    class Meta:
        model = Bookmark
        exclude = ('created', 'modified')
        read_only_fields = ('id', 'person')


class FilmReviewSerializer(serializers.ModelSerializer):
    film = FilmSerializer(many=False, read_only=True)

    class Meta:
        model = FilmReview
        exclude = ('created', 'modified')
        read_only_fields = ('id', 'person')


class FilmReviewDetailSerializer(FilmReviewSerializer):
    score = serializers.FloatField()
    quantity = serializers.IntegerField()


class PersonDetailSerializer(serializers.ModelSerializer):
    last_bookmarks = serializers.SerializerMethodField()
    last_favorites = serializers.SerializerMethodField()
    last_film_reviews = serializers.SerializerMethodField()

    def get_last_bookmarks(self, person):
        return BookmarkSerializer(
            self.context['last_bookmarks'],
            many=True,
            context=self.context,
        ).data

    def get_last_favorites(self, person):
        return FavoriteSerializer(
            self.context['last_favorites'],
            many=True,
            context=self.context,
        ).data

    def get_last_film_reviews(self, person):
        return self.context['last_film_reviews']

    class Meta:
        model = Person
        read_only_fields = ('id',)
        exclude = ('password',)

