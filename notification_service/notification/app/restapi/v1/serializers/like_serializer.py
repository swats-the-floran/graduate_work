from rest_framework import serializers
from restapi.v1.serializers.base import ReceiverBaseSerializer


class LikesSerializer(serializers.Serializer):
    receiver = ReceiverBaseSerializer()
    link = serializers.URLField(required=True)
    count = serializers.IntegerField(min_value=1, required=True)
