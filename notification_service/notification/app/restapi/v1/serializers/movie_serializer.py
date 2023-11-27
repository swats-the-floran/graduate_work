from restapi.v1.serializers.base import MovieBaseSerializer, ReceiverListSerializer


class MovieSerializer(ReceiverListSerializer, MovieBaseSerializer):
    pass
