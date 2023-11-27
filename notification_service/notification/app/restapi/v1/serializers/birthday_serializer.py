from rest_framework import serializers
from restapi.v1.serializers.base import ReceiverListSerializer


class BirthdaySerializer(ReceiverListSerializer):
    message = serializers.CharField(required=False)
