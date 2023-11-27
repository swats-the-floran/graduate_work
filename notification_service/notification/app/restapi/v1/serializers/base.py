from django.core.validators import RegexValidator
from rest_framework import serializers


class ReceiverBaseSerializer(serializers.Serializer):
    """Базовый сериалайзер посетителей"""
    email = serializers.EmailField(max_length=255)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_null=True)
    user_id = serializers.CharField(max_length=36, required=True)  # 36 for uuid

    phone_regex = RegexValidator(
        regex=r'^\+?\d{11}$',
        message="Phone number must be entered in the format: '+79123456789'")

    phone_number = serializers.CharField(validators=[phone_regex], max_length=12, required=False)


class MovieBaseSerializer(serializers.Serializer):
    """Базовый сериалайзер произведений"""
    movie_name = serializers.CharField(max_length=255)
    imdb_rating = serializers.DecimalField(max_digits=2, decimal_places=1, min_value=0)
    movie_link = serializers.URLField()
    movie_description = serializers.CharField()


class ReceiverListSerializer(serializers.Serializer):
    receivers = ReceiverBaseSerializer(many=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        receivers = attrs.get('receivers', None)
        if not receivers:
            raise serializers.ValidationError({'receivers': 'Не может быть пустым!'})

        return attrs
