from rest_framework import serializers
from restapi.v1.serializers.base import MovieBaseSerializer, ReceiverBaseSerializer


class BookmarksSerializer(serializers.Serializer):
    receiver = ReceiverBaseSerializer()
    movies = MovieBaseSerializer(many=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        movies = attrs.get('movies', None)

        if not movies:
            raise serializers.ValidationError({'movies': 'Не должно быть пустым!'})

        return attrs
